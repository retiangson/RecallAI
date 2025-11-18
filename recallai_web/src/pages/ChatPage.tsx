import { useEffect, useState, KeyboardEvent, useRef } from "react";
import { sendChat } from "../api/chatApi";
import { UploadNotes } from "../components/UploadNotes";
import { getConversations, createConversation } from "../api/conversationApi";
import ChatBubble from "../components/ChatBubble";

type MessageRole = "user" | "assistant";

interface Message {
  role: MessageRole;
  content: string;
}

interface Conversation {
  id: number;
  title: string | null;
  messages: Message[];
}

export function ChatPage({ user }: { user: { id: number; email: string } }) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] =
    useState<Conversation | null>(null);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeConversation?.messages, loading]);

  useEffect(() => {
    async function load() {
      try {
        const conv = await getConversations(user.id);

        if (Array.isArray(conv) && conv.length > 0) {
          const normalized = conv.map((c: any) => ({
            id: c.id,
            title: c.title ?? null,
            messages: Array.isArray(c.messages) ? c.messages : [],
          }));
          setConversations(normalized);
          setActiveConversation(normalized[0]);
        } else {
          const created = await createConversation(user.id);
          const newConv = {
            id: created.id,
            title: created.title ?? null,
            messages: [],
          };
          setConversations([newConv]);
          setActiveConversation(newConv);
        }
      } catch (err) {
        console.error("Conversation loading failed:", err);
      }
    }

    load();
  }, [user.id]);

  if (!activeConversation) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#121212] text-gray-300">
        Loading conversations...
      </div>
    );
  }

  async function handleNewConversation() {
    try {
      const created = await createConversation(user.id);
      const newConv = {
        id: created.id,
        title: created.title ?? null,
        messages: [],
      };
      setConversations((prev) => [newConv, ...prev]);
      setActiveConversation(newConv);
    } catch (err) {
      console.error("Failed to create conversation:", err);
    }
  }

  async function handleSend() {
    if (!input.trim() || !activeConversation) return;

    const text = input.trim();
    setInput("");

    const userMsg: Message = { role: "user", content: text };

    const tempConv = {
      ...activeConversation,
      messages: [...activeConversation.messages, userMsg],
    };

    setActiveConversation(tempConv);
    setConversations((prev) =>
      prev.map((c) => (c.id === tempConv.id ? tempConv : c))
    );

    setLoading(true);

    try {
      const response = await sendChat(activeConversation.id, text);
      const aiMsg: Message = { role: "assistant", content: response.answer };

      const finalConv = {
        ...tempConv,
        messages: [...tempConv.messages, aiMsg],
      };

      setActiveConversation(finalConv);
      setConversations((prev) =>
        prev.map((c) => (c.id === finalConv.id ? finalConv : c))
      );
    } catch (err) {
      console.error("Chat failed:", err);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex h-screen bg-[#2a2a2a] text-gray-100 overflow-hidden">

      {/* SIDEBAR */}
      <aside className="w-72 bg-[#202123] border-r border-[#2A2A2A] flex flex-col overflow-hidden">
        <div className="p-4 border-b border-[#2A2A2A]">
          <UploadNotes />
        </div>

        <div className="p-3 border-b border-[#2A2A2A]">
          <button
            onClick={handleNewConversation}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 rounded text-sm"
          >
            + New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-2 text-sm">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className={`p-3 rounded cursor-pointer transition ${
                activeConversation.id === conv.id
                  ? "bg-[#2F2F2F] text-white"
                  : "bg-[#1E1E1E] text-gray-400 hover:bg-[#2F2F2F] hover:text-white"
              }`}
              onClick={() => setActiveConversation(conv)}
            >
              {conv.title || `Conversation ${conv.id}`}
            </div>
          ))}
        </div>
      </aside>

      {/* MAIN CHAT COLUMN */}
      <main className="flex-1 flex flex-col overflow-hidden">

        {/* HEADER */}
        <div className="p-4 border-b border-[#2A2A2A] bg-[#202123] text-sm flex justify-between">
          <div>{activeConversation.title || "Conversation"}</div>
          <div className="text-xs text-gray-400">Logged in as {user.email}</div>
        </div>

        {/* MESSAGES */}
        <div className="flex-1 overflow-y-auto px-5 py-6">
          <div className="max-w-[740px] mx-auto flex flex-col gap-4">

            {activeConversation.messages.map((msg, idx) => (
              <ChatBubble key={idx} role={msg.role} content={msg.content} />
            ))}

            {loading && <ChatBubble role="assistant" content="⏳ Thinking..." />}

            <div ref={bottomRef} />
          </div>
        </div>

        {/* INPUT BAR */}
        <div className="p-4 border-t border-[#2A2A2A] bg-[#202123]">
          <div className="max-w-[740px] mx-auto flex gap-3 w-full">

            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              className="
                flex-1 resize-none px-4 py-3
                rounded-3xl bg-[#1E1E1E] text-gray-100
                border border-[#3A3A3A]
                focus:outline-none focus:ring-2 focus:ring-blue-600
                max-h-48 overflow-y-auto
                placeholder-gray-500
              "
              placeholder="Message RecallAI..."
            />

            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="px-6 py-3 rounded-3xl bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700"
            >
              Send
            </button>

          </div>
        </div>
      </main>
    </div>
  );
}
