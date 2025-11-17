import { useState } from "react";
import { sendChat } from "../api/chatApi";
import { ChatBubble } from "./ChatBubble";

export function ChatWindow() {
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<
    { role: string; content: string }[]
  >([]);
  const [input, setInput] = useState("");

  async function handleSend() {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: input }]);

    const res = await sendChat(conversationId, input);

    if (!conversationId && res.conversation_id) {
      setConversationId(res.conversation_id);
    }

    setMessages((prev) => [...prev, { role: "assistant", content: res.answer }]);
    setInput("");
  }

  return (
    <div className="border p-4 rounded-lg shadow space-y-4">
      <div className="h-80 overflow-y-auto space-y-3">
        {messages.map((m, i) => (
          <ChatBubble key={i} role={m.role} content={m.content} />
        ))}
      </div>

      <div className="flex gap-2">
        <input
          className="flex-1 border rounded p-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask RecallAI..."
        />
        <button
          onClick={handleSend}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Send
        </button>
      </div>
    </div>
  );
}
