import axios from "axios";

export const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "")

// LOGIN
export async function login(email: string, password: string) {
  const res = await axios.post(`${API_BASE}/auth/login`, {
    email,
    password,
  });
  return res.data; // { id, email }
}

// REGISTER
export async function register(email: string, password: string) {
  const res = await axios.post(`${API_BASE}/auth/register`, {
    email,
    password,
  });
  return res.data; // { id, email }
}
