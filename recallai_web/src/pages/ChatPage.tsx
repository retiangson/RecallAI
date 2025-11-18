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

  const [notes, setNotes] = useState<any[]>([]);
  const [showNotes, setShowNotes] = useState(true);
  const [showConversations, setShowConversations] = useState(true);

  const [sidebarOpen, setSidebarOpen] = useState(true);

  const bottomRef = useRef<HTMLDivElement | null>(null);

  /* Auto-scroll */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeConversation?.messages, loading]);

  /* Load conversations */
  useEffect(() => {
    async function load() {
      const conv = await getConversations(user.id);

      if (Array.isArray(conv) && conv.length > 0) {
        const mapped = conv.map((c: any) => ({
          id: c.id,
          title: c.title ?? null,
          messages: Array.isArray(c.messages) ? c.messages : [],
        }));

        setConversations(mapped);
        setActiveConversation(mapped[0]);
      } else {
        const created = await createConversation(user.id);
        const newConv: Conversation = {
          id: created.id,
          title: created.title ?? null,
          messages: [],
        };
        setConversations([newConv]);
        setActiveConversation(newConv);
      }
    }
    load();
  }, [user.id]);

  async function handleNewConversation() {
    const created = await createConversation(user.id);
    const newConv: Conversation = {
      id: created.id,
      title: created.title ?? null,
      messages: [],
    };
    setConversations((prev) => [newConv, ...prev]);
    setActiveConversation(newConv);
  }

  async function handleSend() {
    if (!input.trim() || !activeConversation) return;

    const text = input.trim();
    setInput("");

    const newUserMsg: Message = { role: "user", content: text };

    const tempConv = {
      ...activeConversation,
      messages: [...activeConversation.messages, newUserMsg],
    };

    setActiveConversation(tempConv);
    setConversations((prev) =>
      prev.map((c) => (c.id === tempConv.id ? tempConv : c))
    );

    setLoading(true);

    try {
      const res = await sendChat(activeConversation.id, text);
      const aiMsg: Message = { role: "assistant", content: res.answer };

      const updated = {
        ...tempConv,
        messages: [...tempConv.messages, aiMsg],
      };

      setActiveConversation(updated);
      setConversations((prev) =>
        prev.map((c) => (c.id === updated.id ? updated : c))
      );
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

  if (!activeConversation) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-[#121212] text-gray-300">
        Loading conversations...
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-[#2A2A2A] text-gray-100 flex relative">
      {/* SIDEBAR TOGGLE WHEN HIDDEN */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="absolute top-4 left-4 z-20 bg-[#2F3033] 
                     text-gray-200 px-3 py-2 rounded-lg hover:bg-[#3A3B3F] transition"
        >
          ☰
        </button>
      )}

      {/* SIDEBAR */}
      {sidebarOpen && (
        <aside className="w-[320px] h-full bg-[#1E1F22] border-r border-[#2C2D2F] flex flex-col">
          {/* Sidebar Header */}
          <div className="p-4 border-b border-[#2A2A2A] flex justify-between items-center">
            <h2 className="text-sm font-semibold text-[#E5E7EB]">RecallAI</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-gray-400 hover:text-gray-200"
            >
              ✕
            </button>
          </div>

          {/* Upload Section */}
          <div className="p-4 border-b border-[#2A2A2A]">
            <UploadNotes setNotes={setNotes} />
          </div>

          {/* Notes Section */}
          <div className="border-b border-[#2A2A2A]">
            <button
              onClick={() => setShowNotes(!showNotes)}
              className="w-full px-4 py-3 flex justify-between items-center bg-[#2A2C2F] text-[#E5E7EB] text-sm hover:bg-[#2A2C2F] transition"
            >
              <span>Notes</span>
              <span className="text-gray-400">{showNotes ? "▾" : "▸"}</span>
            </button>

            {showNotes && (
              <div className="px-4 py-2 max-h-56 overflow-y-auto space-y-2">
                {notes.length === 0 && (
                  <p className="text-xs text-gray-500">
                    No notes uploaded yet
                  </p>
                )}

                {notes.map((note) => (
                  <div
                    key={note.id}
                    className="p-3 rounded bg-[#1E1E1E] text-gray-300 border border-[#333]"
                  >
                    {note.title}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Messages Section */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <button
              onClick={() => setShowConversations(!showConversations)}
              className="w-full px-4 py-3 flex justify-between items-center bg-[#2A2C2F] text-[#E5E7EB] text-sm hover:bg-[#2A2C2F] transition border-b border-[#2C2D2F]"
            >
              <span className="font-medium">Messages</span>
              <span className="text-gray-400">
                {showConversations ? "▾" : "▸"}
              </span>
            </button>

            {showConversations && (
              <div className="flex-1 overflow-y-auto p-3 space-y-2">
                <button
                  onClick={handleNewConversation}
                  className="w-full bg-green-300 text-green-900 py-2 rounded-full text-sm font-medium hover:bg-green-400 transition shadow-sm"
                >
                  + New Chat
                </button>

                {conversations.map((conv) => (
                  <div
                    key={conv.id}
                    onClick={() => setActiveConversation(conv)}
                    className={`p-3 rounded cursor-pointer transition
                      ${
                        activeConversation.id === conv.id
                          ? "bg-[#2A2C2F] text-white py-2 rounded-full shadow-sm"
                          : "bg-[#1E1F22] text-gray-400 hover:bg-[#2A2C2F] hover:text-white py-2 rounded-full shadow-sm"
                      }
                    `}
                  >
                    {conv.title || `Conversation ${conv.id}`}
                  </div>
                ))}
              </div>
            )}
          </div>
        </aside>
      )}

      {/* RIGHT SIDE: HEADER + CONTENT + FOOTER */}
      <div className="flex-1 flex flex-col h-full">
        {/* HEADER */}
        <header className="h-16 flex items-center justify-between px-6 bg-[#202123] border-b border-[#2C2D2F] shadow-md">
          <div className="flex items-center gap-4">
            <span className="text-lg font-semibold text-white">RecallAI</span>
            <span className="text-sm text-gray-300 opacity-80">
              {activeConversation.title || "Conversation"}
            </span>
          </div>
          <div className="text-xs text-gray-400">Logged in as {user.email}</div>
        </header>

        {/* MESSAGES (SCROLLABLE MIDDLE) */}
        <main className="flex-1 overflow-y-auto px-5 py-6">
          <div className="max-w-[740px] mx-auto flex flex-col gap-4">
            {activeConversation.messages.map((msg, idx) => (
              <ChatBubble key={idx} role={msg.role} content={msg.content} />
            ))}

            {loading && (
              <ChatBubble role="assistant" content="⏳ Thinking..." />
            )}

            <div ref={bottomRef} />
          </div>
        </main>

        {/* FOOTER / INPUT BAR */}
        <footer className="border-t border-[#2C2D2F] bg-[#202123] p-4">
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
              className="
                px-6 py-3 rounded-3xl
                bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700
              "
            >
              Send
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}
