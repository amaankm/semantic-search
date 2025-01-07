import { initPinecone } from "~/utils/pinecone";
import { getEmbedding } from "~/utils/embedding";

export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const { text, metadata } = body;

  const pinecone = await initPinecone();
  const index = pinecone.index("semantic-search");

  const embedding = await getEmbedding(text);

  await index.upsert([
    {
      id: metadata.id,
      values: embedding,
      metadata,
    },
  ]);

  return { success: true };
});
