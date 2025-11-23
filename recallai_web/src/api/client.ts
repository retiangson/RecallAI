import axios from "axios";

// Load backend URL from Vite .env
export const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "")
  
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

// =================================================================
// Conversation APIs
// =================================================================

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

export async function renameConversation(conversation_id: number, title: string) {
  const res = await client.post("/conversation/rename", {
    conversation_id,
    title,
  });
  return res.data;
}

export async function deleteConversation(conversation_id: number) {
  const res = await client.post("/conversation/delete", {
    conversation_id,
  });
  return res.data;
}

// =================================================================
// Notes APIs (NEW)
// =================================================================

// ⭐ Create a note
export async function createNote(
  user_id: number,
  title: string | null,
  content: string,
  source: string | null = null
) {
  const res = await client.post("/notes", {
    user_id,
    title,
    content,
    source,
  });
  return res.data; // NoteResponseDTO
}

// ⭐ Get one note
export async function getNote(note_id: number) {
  const res = await client.post("/notes/get", { note_id });
  return res.data; // NoteResponseDTO | null
}

// ⭐ List notes for a user
export async function listNotes(user_id: number) {
  const res = await client.post("/notes/list", { user_id });
  return res.data; // NoteResponseDTO[]
}

// ⭐ Update a note
export async function updateNote(
  note_id: number,
  title?: string | null,
  content?: string | null
) {
  const res = await client.post("/notes/update", {
    note_id,
    title: title ?? null,
    content: content ?? null,
  });
  return res.data; // NoteResponseDTO | null
}

// ⭐ Delete a note
export async function deleteNote(note_id: number) {
  const res = await client.post("/notes/delete", { note_id });
  return res.data; // bool
}

// ⭐ Vector Search Notes
export async function searchNotes(vector: number[], top_k: number = 5) {
  const res = await client.post("/notes/search", { vector, top_k });
  return res.data; // NoteResponseDTO[]
}
