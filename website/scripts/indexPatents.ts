import { createReadStream } from "fs";
import { parse } from "csv-parse";
import { initPinecone } from "../utils/pinecone";
import { getEmbedding } from "../utils/embedding";

async function indexPatents() {
  const pinecone = await initPinecone();
  const index = pinecone.index("semantic-search");

  // Batch size for uploading to Pinecone
  const BATCH_SIZE = 100;
  let batch = [];

  const parser = createReadStream("../patents.tsv").pipe(
    parse({
      delimiter: "\t",
      columns: true,
      skip_empty_lines: true,
    })
  );

  for await (const record of parser) {
    const embedding = await getEmbedding(record.patent_abstract);

    batch.push({
      id: record.patent_id,
      values: embedding,
      metadata: {
        patent_id: record.patent_id,
        abstract: record.patent_abstract,
      },
    });

    if (batch.length >= BATCH_SIZE) {
      await index.upsert(batch);
      console.log(`Indexed ${batch.length} patents`);
      batch = [];
    }
  }

  // Index remaining patents
  if (batch.length > 0) {
    await index.upsert(batch);
    console.log(`Indexed final ${batch.length} patents`);
  }
}

// Run the indexing
indexPatents().catch(console.error);
