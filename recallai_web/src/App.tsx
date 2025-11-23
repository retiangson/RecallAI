import { useState } from "react";
import { getUser } from "./utils/auth";
import { ChatPage } from "./pages/ChatPage";
import { LoginPage } from "./pages/LoginPage";

export default function App() {
  // -----------------------------------------------
  // Load current user from local storage/session.
  // If no user is logged in, getUser() returns null.
  // -----------------------------------------------
  const [user, setUser] = useState<{ id: number; email: string } | null>(getUser());

  // ---------------------------------------------------------
  // Called after successful login (LoginPage → onLogin callback).
  // Refreshes the user state by re-reading the stored user info.
  // ---------------------------------------------------------
  function refreshUser() {
    setUser(getUser());
  }

  // ---------------------------------------------------
  // If there is NO logged-in user:
  // Render the LoginPage and pass a handler (onLogin)
  // so LoginPage can notify App to refresh the user state.
  // ---------------------------------------------------
  if (!user) {
    return (
      <div className="app-shell">
        <LoginPage onLogin={refreshUser} />
      </div>
    );
  }

  // ----------------------------------------------------
  // If the user IS logged in:
  // Render the ChatPage and pass the user object as props.
  // ----------------------------------------------------
  return (
    <div className="app-shell">
      <ChatPage user={user} />
    </div>
  );
}
