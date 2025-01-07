import { Pinecone } from "@pinecone-database/pinecone";
import dotenv from "dotenv";
dotenv.config();

export const initPinecone = async () => {
  const pc = new Pinecone({
    apiKey: process.env.PINECONE_API_KEY!,
  });
  return pc;
};
