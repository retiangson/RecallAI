import { useState } from "react";
import { login, register } from "../api/authApi";
import { saveUser } from "../utils/auth";

export function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit() {
    setError("");

    // ---------------------------
    // Confirm password validation
    // ---------------------------
    if (mode === "register" && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      if (mode === "register") {
        await register(email, password);
      }

      const user = await login(email, password);
      saveUser(user);
      onLogin();
    } catch (err) {
      setError(
        mode === "login"
          ? "Invalid login credentials."
          : "Registration failed. Email may already exist."
      );
    }
  }

  return (
    <div className="h-screen flex items-center justify-center bg-gray-900">
      <div className="bg-gray-800 p-6 rounded-lg shadow-md w-80">
        <h2 className="text-lg mb-4 text-white text-center">
          {mode === "login" ? "Login" : "Register"}
        </h2>

        <input
          className="w-full mb-3 p-2 rounded bg-gray-700 text-white"
          placeholder="Email"
          type="email"
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

        {/* Show confirm password ONLY in register mode */}
        {mode === "register" && (
          <input
            className="w-full mb-3 p-2 rounded bg-gray-700 text-white"
            placeholder="Confirm Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        )}

        {error && <p className="text-red-400 text-sm mb-2">{error}</p>}

        <button
          onClick={handleSubmit}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-500"
        >
          {mode === "login" ? "Login" : "Create Account"}
        </button>

        <button
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError("");
          }}
          className="w-full text-sm text-gray-300 mt-3 underline"
        >
          {mode === "login"
            ? "Need an account? Register"
            : "Already have an account? Login"}
        </button>
      </div>
    </div>
  );
}
