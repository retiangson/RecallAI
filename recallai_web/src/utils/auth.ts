export function saveUser(user: { id: number; email: string } | null) {
  localStorage.setItem("recallai_user", JSON.stringify(user));
}

export function getUser() {
  const raw = localStorage.getItem("recallai_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function logout() {
  localStorage.removeItem("recallai_user");
}
