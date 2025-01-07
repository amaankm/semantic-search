import { initPinecone } from "~/utils/pinecone";
import { getEmbedding } from "~/utils/embedding";

interface SearchParams {
  q: string;
  limit?: string;
}

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event) as SearchParams;

    if (!query.q?.trim()) {
      throw createError({
        statusCode: 400,
        message: "Search query is required",
      });
    }

    const pinecone = await initPinecone();
    const index = pinecone.index("semantic-search");
    const embedding = await getEmbedding(query.q);

    const results = await index.query({
      vector: embedding,
      topK: parseInt(query.limit || "10"),
      includeMetadata: true,
    });

    return results.matches;
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      message: error.message || "Failed to perform search",
    });
  }
});
