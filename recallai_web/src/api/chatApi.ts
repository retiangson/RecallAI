import axios from "axios";

// Normalize base URL, remove any trailing slash
const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1")
  .replace(/\/+$/, "");

// Reusable axios client
export const api = axios.create({
  baseURL: API_BASE,
});

// ------------------------------
// SEND CHAT MESSAGE
// ------------------------------
export async function sendChat(
  conversation_id: number,
  prompt: string,
  top_k: number = 5
) {
  const response = await api.post("/chat", {
    conversation_id,
    prompt,
    top_k,
  });

  return response.data; // ChatResponseDTO
}

// ------------------------------
// UPLOAD NOTES (txt + zip)
// ------------------------------
// ✔ FIXED: user_id MUST be in the query string
// ✔ FIXED: DO NOT send user_id inside FormData
export async function uploadNotes(files: File[], user_id: number) {
  const formData = new FormData();

  files.forEach((file) => formData.append("files", file));

  // ❗ FastAPI REQUIRES user_id in query params, NOT formData
  const response = await api.post(`/notes/bulk?user_id=${user_id}`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data; // List<NoteResponseDTO>
}
