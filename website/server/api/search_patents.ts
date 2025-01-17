import { initMilvus } from "~/utils/milvus";
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

    const milvus = await initMilvus();

    const embedding = await getEmbedding(query.q);

    const results = await milvus.search({
      collection_name: "patent_abstracts",
      data: embedding,
      limit: 10,
    });

    return results.results;
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      message: error.message || "Failed to perform search",
    });
  }
});
