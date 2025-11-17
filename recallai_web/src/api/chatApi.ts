import axios from "axios";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export async function sendChat(conversationId: number | null, question: string) {
  const response = await axios.post(`${API_BASE}/chat`, {
    conversation_id: conversationId,
    question,
  });

  return response.data;
}

export async function uploadNotes(files: File[]) {
  const formData = new FormData();
  files.forEach((f) => formData.append("files", f));

  const response = await axios.post(`${API_BASE}/notes/bulk`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
}
