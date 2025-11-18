import { useState } from "react";
import { getUser } from "./utils/auth";
import { ChatPage } from "./pages/ChatPage";
import { LoginPage } from "./pages/LoginPage";

export default function App() {
  const [user, setUser] = useState(getUser());

  function refreshUser() {
    setUser(getUser());
  }

  if (!user) {
    return <LoginPage onLogin={refreshUser} />;
  }

  return <ChatPage user={user} />;
}
