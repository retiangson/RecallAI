import axios from "axios";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

// ⭐ Load all conversations for the logged-in user
export async function getConversations(user_id: number) {
  const res = await axios.post(`${API_BASE}/conversation/list`, {
    user_id,
  });
  return res.data;  // [{ id, title, messages: [] }]
}

// ⭐ Create a new conversation
export async function createConversation(user_id: number) {
  const res = await axios.post(`${API_BASE}/conversation/create`, {
    user_id,
  });
  return res.data;  // { id, title }
}

// ⭐ Get messages for a conversation
export async function getConversationMessages(conversation_id: number) {
  const res = await axios.post(`${API_BASE}/conversation/messages`, {
    conversation_id,
  });
  return res.data; // [{ role, content, created_at }]
}

// ⭐ Rename a conversation
export async function renameConversation(conversation_id: number, title: string) {
  const res = await axios.post(`${API_BASE}/conversation/rename`, {
    conversation_id,
    title,
  });
  return res.data;
}

// ⭐ Delete a conversation
export async function deleteConversation(conversation_id: number) {
  const res = await axios.post(`${API_BASE}/conversation/delete`, {
    conversation_id,
  });
  return res.data;
}
