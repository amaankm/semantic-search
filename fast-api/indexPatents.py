import torch
from sentence_transformers import SentenceTransformer
from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, DataType, Collection
)
import pandas as pd
from tqdm import tqdm  # For progress tracking

# Constants
FILE_PATH = "../patents.tsv"
BATCH_SIZE = 1000
VECTOR_DIMENSION = 384  # For all-MiniLM-L6-v2

# Load the data
data = pd.read_csv(FILE_PATH, sep="\t")

print(torch.cuda.is_available())  # This should return True if the GPU is accessible
print(torch.cuda.current_device())  # This should give the device ID (e.g., 0 for the first GPU)
print(torch.cuda.get_device_name(0))  # This will print the GPU name

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Initialize the SentenceTransformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device)

# Connect to Milvus
connections.connect("default", host="localhost", port="19530")

# Define a schema for the Milvus collection
fields = [
    FieldSchema(name="patentID", dtype=DataType.INT64, is_primary=True, auto_id=False),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIMENSION)
]
schema = CollectionSchema(fields, description="Patent Abstracts Collection")

# Create a collection
collection_name = "patent_abstracts"
collection = Collection(name=collection_name, schema=schema)

num_rows = 100000

for start in tqdm(range(0, num_rows, BATCH_SIZE), desc="Processing Batches"):
    # Get batch data
    end = min(start + BATCH_SIZE, num_rows)
    batch = data.iloc[start:end]

    # Encode abstracts
    abstracts = batch['patent_abstract'].tolist()
    vectors = model.encode(abstracts, show_progress_bar=False)

    # Insert into Milvus
    patent_ids = batch['patent_id'].tolist()
    entities = [
        patent_ids,
        vectors
    ]
    # Insert and check for success
    collection.insert(entities)

# Index the collection for faster searching (if not already indexed)
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "COSINE",
    "params": {"nlist": 128}
}
if not collection.has_index(field_name="vector"):
    collection.create_index(field_name="vector", index_params=index_params)

# Verify insertion
print(f"Total number of entries in the collection: {collection.num_entities}")