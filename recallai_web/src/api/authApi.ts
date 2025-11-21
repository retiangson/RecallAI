import axios from "axios";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "https://txerft5ftb.execute-api.ap-southeast-2.amazonaws.com/Prod/api";
  //import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
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
