import axios from "axios";

export const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "")
  
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

  let messages = res.data || [];

  // Sort reliably
  messages.sort((a: any, b: any) => {
    // If ID exists, use it
    if (a.id && b.id) return a.id - b.id;

    // Otherwise sort by timestamp
    if (a.created_at && b.created_at) {
      return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
    }

    return 0; // fallback
  });

  return messages;
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
