import { useState } from "react";
import { login, register } from "../api/authApi";
import { saveUser } from "../utils/auth";
import Logo from "../assets/recallai_logo.png"; // <-- Put your logo here

export function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit() {
    setError("");

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
    <div className="h-screen w-screen flex bg-gray-900 text-white">

      {/* LEFT PANEL - LOGIN FORM */}
      <div className="flex flex-col justify-center items-center w-full md:w-1/2 p-8">
        <div className="bg-gray-800 p-8 rounded-2xl shadow-lg w-full max-w-sm">
          <h2 className="text-2xl font-semibold mb-6 text-center">
            {mode === "login" ? "Welcome Back" : "Create Account"}
          </h2>

          <input
            className="w-full mb-3 p-3 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            className="w-full mb-3 p-3 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {mode === "register" && (
            <input
              className="w-full mb-3 p-3 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Confirm Password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          )}

          {error && <p className="text-red-400 text-sm mb-2">{error}</p>}

          <button
            onClick={handleSubmit}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-500 transition"
          >
            {mode === "login" ? "Login" : "Create Account"}
          </button>

          <button
            onClick={() => {
              setMode(mode === "login" ? "register" : "login");
              setError("");
            }}
            className="w-full text-sm text-gray-300 mt-4 underline hover:text-white"
          >
            {mode === "login"
              ? "Need an account? Register"
              : "Already have an account? Login"}
          </button>
        </div>
      </div>

      {/* RIGHT PANEL - LOGO + IMAGE + DETAILS */}
      <div className="hidden md:flex flex-col justify-center items-center w-1/2 p-10 bg-gradient-to-br from-[#0f172a] to-[#1e3a8a] relative overflow-hidden">

        {/* Background Image */}
        <div className="absolute inset-0 opacity-30">
          <img
            src="https://images.unsplash.com/photo-1526378722370-1d6fe622e3e2?auto=format&fit=crop&w=1200&q=80"
            alt="background"
            className="w-full h-full object-cover"
          />
        </div>

        {/* Overlay */}
        <div className="absolute inset-0 bg-black bg-opacity-40"></div>

        {/* Content */}
        <div className="relative z-10 text-center px-6">

          {/* Logo */}
          <img
            src={Logo}
            className="mx-auto w-24 h-24 mb-4 drop-shadow-lg"
            alt="RecallAI"
          />

          <h1 className="text-3xl font-bold tracking-wide mb-3">
            RecallAI
          </h1>

          <p className="text-gray-300 max-w-md mx-auto leading-relaxed">
            Smart memory assistant for your notes, conversations, screenshots,
            documents and daily knowledge.  
            Powered by advanced AI and your own personal knowledge base.
          </p>
        </div>
      </div>
    </div>
  );
}
