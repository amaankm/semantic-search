export const getEmbedding = async (text: string): Promise<number[]> => {
  const response = await fetch("http://localhost:8080/embed", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error("Failed to generate embedding");
  }

  return response.json();
};
