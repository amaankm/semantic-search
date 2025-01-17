import { MilvusClient } from "@zilliz/milvus2-sdk-node";

export const initMilvus = async () => {
  const address = "http://localhost:19530";
  const token = "root:Milvus";
  const client = new MilvusClient({
    address,
    token,
  });
  return client;
};
