import { useState } from "react";
import { login } from "../api/authApi";
import { saveUser } from "../utils/auth";

export function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleLogin() {
    try {
      const user = await login(email, password);
      saveUser(user);
      onLogin();
    } catch {
      setError("Invalid login credentials.");
    }
  }

  return (
    <div className="h-screen flex items-center justify-center bg-gray-900">
      <div className="bg-gray-800 p-6 rounded-lg shadow-md w-80">
        <h2 className="text-lg mb-4 text-white text-center">Login</h2>

        <input
          className="w-full mb-3 p-2 rounded bg-gray-700 text-white"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          className="w-full mb-3 p-2 rounded bg-gray-700 text-white"
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <p className="text-red-400 text-sm mb-2">{error}</p>}

        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-500"
        >
          Login
        </button>
      </div>
    </div>
  );
}
