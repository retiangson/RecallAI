import axios from "axios";

// Load backend URL from Vite .env
const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

// Axios client
export const client = axios.create({
  baseURL: API_BASE,
});

// --------------------
// Chat API
// --------------------
export async function askRecallAI(conversation_id: number, question: string) {
  const res = await client.post("/chat", {
    conversation_id,
    question,
    top_k: 5,
  });
  return res.data; // ChatResponseDTO
}

// --------------------
// Notes Upload API
// --------------------
export async function uploadNotes(
  files: File[],
  user_id: number
): Promise<any> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  formData.append("user_id", String(user_id));

  const res = await client.post("/notes/bulk", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

// --------------------
// Conversation APIs
// --------------------
export async function getConversations(user_id: number) {
  const res = await client.post("/conversation/list", { user_id });
  return res.data;
}

export async function createConversation(user_id: number) {
  const res = await client.post("/conversation/create", { user_id });
  return res.data;
}

export async function getMessages(conversation_id: number) {
  const res = await client.post("/conversation/messages", { conversation_id });
  return res.data;
}

