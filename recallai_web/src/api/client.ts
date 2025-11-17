import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE,
});

// Ask RecallAI
export async function askRecallAI(question: string) {
  const res = await api.post("/chat", { question, top_k: 5 });
  return res.data;
}

// Upload multiple .txt or .zip
export async function uploadNotes(files: File[]) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const res = await api.post("/notes/bulk", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}
