import requests
import torch
import json
from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType
import pandas as pd
from tqdm import tqdm

# Constants
BASE_URL = "https://api.openalex.org/works"
PARAMS = {
    "sort": "publication_year:desc",
    "filter": "cited_by_count:>1000,language:en,has_abstract:true,type:article",
    "per-page": "200",  # Fetch 200 records per page
    "cursor": "*",      # Start with the first page
}

def reconstruct_text(inverted_index):
    # Determine the maximum position
    max_pos = max(pos for positions in inverted_index.values() for pos in positions)
    
    # Create an array to hold words at their respective positions
    reconstructed = [""] * (max_pos + 1)
    
    # Place words at their positions
    for word, positions in inverted_index.items():
        for pos in positions:
            reconstructed[pos] = word
    
    # Join the words to form the reconstructed text
    return " ".join(filter(None, reconstructed))


print(torch.cuda.is_available())  # This should return True if the GPU is accessible
print(torch.cuda.current_device())  # This should give the device ID (e.g., 0 for the first GPU)
print(torch.cuda.get_device_name(0))  # This will print the GPU name

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Initialize the SentenceTransformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device)

milvus_host = "localhost"  # change this if using a remote server
milvus_port = "19530"  # default port for Milvus
collection_name = "papers_collection"

# Initialize Milvus connection
connections.connect("default", host=milvus_host, port=milvus_port)

# Step 6: Define Milvus Schema
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, description="Paper ID", max_length=64),
    FieldSchema(name="title", dtype=DataType.VARCHAR, description="Title of the paper", max_length=1024),
    FieldSchema(name="publication_year", dtype=DataType.INT64, description="Publication Year"),
    FieldSchema(name="landing_page_url", dtype=DataType.VARCHAR, description="Landing Page URL", max_length=1024),
    FieldSchema(name="host_organization_name", dtype=DataType.VARCHAR, description="Host Organization Name", max_length=1024),
    FieldSchema(name="cited_by_count", dtype=DataType.INT64, description="Number of citations"),
    FieldSchema(name="abstract", dtype=DataType.VARCHAR, description="Article Abstarct", max_length=4096),
    FieldSchema(name="abstract_vector", dtype=DataType.FLOAT_VECTOR, dim=384, description="Sentence embeddings of abstract"),
]

schema = CollectionSchema(fields, description="Papers Collection")
collection = Collection(name=collection_name, schema=schema)

batch_size = 200  # Set the batch size for processing

for i in tqdm(range(0, 50000, batch_size), desc="Processing Batches"):
    
    response = requests.get(BASE_URL, params=PARAMS)
    response.raise_for_status()  # Raise exception for HTTP errors
    data = response.json()
    
    # Extract results and metadata
    papers = data.get("results", [])
    next_cursor = data.get("meta", {}).get("next_cursor", None)

    metadata = []
    abstracts = []

    for paper in papers:
        abstract_text = reconstruct_text(paper['abstract_inverted_index'])
        
        # Add required information for each paper
        metadata.append({
            'id': paper['id'],
            'title': paper['title'] if paper.get('title') else "",
            'publication_year': paper['publication_year'],
            'landing_page_url': (
                        paper["primary_location"]["landing_page_url"]
                        if paper.get("primary_location") and paper["primary_location"].get("landing_page_url")
                        else ""
                    ),
            'host_organization_name': (
                        paper["primary_location"]["source"]["host_organization_name"]
                        if paper.get("primary_location") and paper["primary_location"].get("source") and paper["primary_location"]["source"].get("host_organization_name")
                        else ""
                    ),
            'cited_by_count': paper['cited_by_count'],
            'abstract': abstract_text.encode('utf-8')[:4000].decode('utf-8', 'ignore')  # abstract text for processing
        })
        
        # Add abstract text to process later
        abstracts.append(abstract_text)

    embeddings = model.encode(abstracts, show_progress_bar=False)

    insert_data = [
        [paper['id'] for paper in metadata],  # ids
        [paper['title'] for paper in metadata],  # titles
        [paper['publication_year'] for paper in metadata],  # publication_year
        [paper['landing_page_url'] for paper in metadata],  # landing_page_urls
        [paper['host_organization_name'] for paper in metadata],  # host_organization_names
        [paper['cited_by_count'] for paper in metadata],  # cited_by_count
        [paper['abstract'] for paper in metadata],  # abstract
        embeddings.tolist()  # abstract_vectors (embeddings)
    ]

    collection.insert(insert_data)

    PARAMS["cursor"] = next_cursor

    print(next_cursor)


collection.create_index(field_name="abstract_vector", index_params={"index_type": "IVF_FLAT","metric_type": "COSINE", "params": {"nlist": 100}})

print("Data inserted successfully into Milvus!")
