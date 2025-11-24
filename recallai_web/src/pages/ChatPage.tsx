import { saveUser } from "../utils/auth";
import React, { useEffect, useState, KeyboardEvent, useRef } from "react";
import { sendChat, uploadChat } from "../api/chatApi";
import {
  listNotes,
  deleteNote,
  updateNote,
  createNote,
  getNote,
} from "../api/client";
import { UploadNotes } from "../components/UploadNotes";
import {
  getConversations,
  getConversationMessages,
  createConversation,
  deleteConversation,
  renameConversation,
  addMessageToNoteAPI,
  deleteMessage,
  getConversationMessagesPaginated,
} from "../api/conversationApi";
import ChatBubble from "../components/ChatBubble";

type MessageRole = "user" | "assistant";

interface Message {
  id: number;
  role: MessageRole;
  content: string;
}

interface Conversation {
  id: number;
  title: string | null;
  messages: Message[];
}

export function ChatPage({ user }: { user: { id: number; email: string } }) {
  const TEMP_CONVERSATION_ID = -1;



  const attachmentInputRef = useRef<HTMLInputElement | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] =
    useState<Conversation | null>(null);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);

  const [messagesLimit] = useState(10);
  const [messagesCursor, setMessagesCursor] = useState<number | null>(null);
  
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ id: number, content: string, index: number } | null>(null);

  const [notes, setNotes] = useState<any[]>([]);

  const [showNotes, setShowNotes] = useState(true);
  const [showConversations, setShowConversations] = useState(true);

  const [sidebarOpen, setSidebarOpen] = useState(true);

  // NOTE EDITOR STATE
  const [selectedNote, setSelectedNote] = useState<any | null>(null);
  const [noteTitleDraft, setNoteTitleDraft] = useState("");
  const [noteContentDraft, setNoteContentDraft] = useState("");
  const [isNoteDirty, setIsNoteDirty] = useState(false);
  const isProgrammingNoteChange = useRef(false);

  // RESIZABLE NOTE PANEL
  const [notePanelWidth, setNotePanelWidth] = useState(380); // px
  const isResizingNotePanel = useRef(false);
  const layoutRef = useRef<HTMLDivElement | null>(null);

  const bottomRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const messagesContainerRef = useRef<HTMLDivElement | null>(null);

  const [activeNoteMenuData, setActiveNoteMenuData] = useState<{
    type: "note" | "conversation",
    item: any,
    top: number,
    left: number
  } | null>(null);

  function autoResize() {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${el.scrollHeight}px`;
    }
  }

  function handleDropFile(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files || []);
    if (!files.length) return;
    setPendingFiles((prev) => [...prev, ...files]);
  }

 // Open / load a note into right editor panel
  async function openNoteEditor(note: any) {
    // always fetch the latest from backend
    const fresh = await getNote(note.id);

    setSelectedNote(fresh);
    setNoteTitleDraft(fresh.title ?? "");
    setNoteContentDraft(fresh.content ?? "");
    setIsNoteDirty(false);
  }

  async function handleDeleteNote(noteId: number) {
    if (!confirm("Delete this note?")) return;

    await deleteNote(noteId);

    setNotes((prev) => prev.filter((n) => n.id !== noteId));
    if (selectedNote?.id === noteId) {
      setSelectedNote(null);
      setNoteTitleDraft("");
      setNoteContentDraft("");
      setIsNoteDirty(false);
    }
  }

  async function handleEditNote(note: any) {
    // No prompt — just open note editor panel
    openNoteEditor(note);
  }

  async function handleSaveNote() {
    if (!noteTitleDraft.trim() && !noteContentDraft.trim()) {
      alert("Cannot save an empty note.");
      return;
    }

    // NEW NOTE
    if (selectedNote?.id === null) {
      const created = await createNote(
        user.id,
        noteTitleDraft,
        noteContentDraft,
        "manual"
      );
      const fresh = await getNote(created.id);

      setNotes((prev) => [fresh, ...prev]);
      setSelectedNote(fresh);
      return;
    }

    // EXISTING NOTE
    await updateNote(selectedNote.id, noteTitleDraft, noteContentDraft);
    const fresh = await getNote(selectedNote.id);

    setNotes((prev) => prev.map((n) => (n.id === fresh.id ? fresh : n)));
    setSelectedNote(fresh);
  }


  function handleDiscardNoteChanges() {
    if (!selectedNote) return;
    setNoteTitleDraft(selectedNote.title ?? "");
    setNoteContentDraft(selectedNote.content ?? "");
    setIsNoteDirty(false);
  }

  async function loadMessages(conversationId: number, loadOlder = false) {
    const res: Message[] = await getConversationMessagesPaginated(
      conversationId,
      10,
      loadOlder ? messagesCursor ?? undefined : undefined
    );

    // Always sort oldest → newest
    const pageAsc = [...res].sort((a, b) => a.id - b.id);

    // FIRST LOAD
    if (!loadOlder) {
      setActiveConversation(prev =>
        prev ? { ...prev, messages: pageAsc } : null
      );

      // Cursor = oldest in page
      if (pageAsc.length > 0) {
        setMessagesCursor(pageAsc[0].id);
      }

      // Auto-scroll to bottom ONLY FIRST TIME
      requestAnimationFrame(() => {
        bottomRef.current?.scrollIntoView({ behavior: "auto" });
      });

      return;
    }

    /*
    * LOAD OLDER — PREPEND + PRESERVE SCROLL PERFECTLY
    */

    const container = messagesContainerRef.current;
    if (!container) return;

    // Record BEFORE sizes
    const prevScrollTop = container.scrollTop;
    const prevScrollHeight = container.scrollHeight;

    setActiveConversation(prev => {
      if (!prev) return null;

      const existingIds = new Set(prev.messages.map(m => m.id));
      const newMessages = pageAsc.filter(m => !existingIds.has(m.id));

      // PREPEND new (older) messages
      return {
        ...prev,
        messages: [...newMessages, ...prev.messages]
      };
    });

    // AFTER DOM updates
    requestAnimationFrame(() => {
      const newScrollHeight = container.scrollHeight;

      // ⭐ Correct formula:
      const diff = newScrollHeight - prevScrollHeight;

      container.scrollTop = prevScrollTop + diff;
    });

    // Update cursor
    if (pageAsc.length > 0) {
      setMessagesCursor(pageAsc[0].id);
    }
  }

  // RESIZE NOTE PANEL
  function startNotePanelResize() {
    isResizingNotePanel.current = true;
  }

  useEffect(() => {
    function handleMouseMove(e: MouseEvent) {
      if (!isResizingNotePanel.current || !layoutRef.current) return;

      const rect = layoutRef.current.getBoundingClientRect();
      const minPanelWidth = 260;
      const maxPanelWidth = rect.width - 320; // keep some space for messages

      const newWidth = rect.right - e.clientX;
      const clamped = Math.min(Math.max(newWidth, minPanelWidth), maxPanelWidth);
      setNotePanelWidth(clamped);
    }

    function handleMouseUp() {
      isResizingNotePanel.current = false;
    }

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, []);

  useEffect(() => {
    if (!selectedNote) {
      setIsNoteDirty(false);
      return;
    }

    const isChanged =
      (noteTitleDraft ?? "") !== (selectedNote.title ?? "") ||
      (noteContentDraft ?? "") !== (selectedNote.content ?? "");

    setIsNoteDirty(isChanged);
  }, [noteTitleDraft, noteContentDraft, selectedNote]);

  /* Load conversations only on first mount */
  useEffect(() => {
    async function load() {
      const convs = await getConversations(user.id);

      if (Array.isArray(convs) && convs.length > 0) {
        const mapped = convs
          .map((c: any) => ({
            id: c.id,
            title: c.title ?? null,
            messages: [],
          }))
          .sort((a, b) => b.id - a.id); // newest first

        setConversations(mapped);

        // ⭐ ONLY set activeConversation if none is selected
        setActiveConversation((prev) => prev ?? mapped[0]);

        // ⭐ ONLY load messages if this is the first load
        if (!activeConversation) {
          await loadMessages(mapped[0].id);
        }
      } else {
        const created = await createConversation(user.id);

        const newConv: Conversation = {
          id: created.id,
          title: created.title ?? null,
          messages: [],
        };

        setConversations([newConv]);

        // Same rule: only set initial activeConversation
        setActiveConversation((prev) => prev ?? newConv);
      }
    }

    load();
  }, []); //REMOVE user.id from dependency array


  useEffect(() => {
    async function loadNotes() {
      const result = await listNotes(user.id);
      setNotes(result);
    }
    loadNotes();
  }, [user.id]);

  useEffect(() => {
    const closeMenu = () => setActiveNoteMenuData(null);
    window.addEventListener("click", closeMenu);
    return () => window.removeEventListener("click", closeMenu);
  }, []);

  async function handleNewNote() {
    // Create an empty draft note (not saved yet)
    const draft = {
      id: null,      // important: null = NEW unsaved note
      title: "",
      content: "",
    };

    setSelectedNote(draft);
    setNoteTitleDraft("");
    setNoteContentDraft("");
  }

  async function handleNewConversation() {
    if (
      activeConversation &&
      activeConversation.id === TEMP_CONVERSATION_ID &&
      activeConversation.messages.length === 0
    ) {
      textareaRef.current?.focus();
      return;
    }

    const tempConv: Conversation = {
      id: TEMP_CONVERSATION_ID,
      title: null,
      messages: [],
    };

    setActiveConversation(tempConv);
    setInput("");

    setTimeout(() => {
      textareaRef.current?.focus();
    }, 0);
  }

  
  async function handleSend() {
    const trimmed = input.trim();
    const hasText = trimmed.length > 0;
    const hasFiles = pendingFiles.length > 0;

    if (!hasText && !hasFiles) return;

    setInput("");
    setLoading(true);

    try {
      let conv = activeConversation;
      let conversationId: number;

      // 1. Ensure conversation exists
      if (!conv || conv.id === TEMP_CONVERSATION_ID) {
        const created = await createConversation(user.id);
        conversationId = created.id;

        const titleSource =
          trimmed || (pendingFiles[0]?.name ?? "New conversation");

        const titleFromFirstMessage =
          titleSource.length > 60
            ? titleSource.slice(0, 57) + "..."
            : titleSource;

        await renameConversation(conversationId, titleFromFirstMessage);

        const newConv: Conversation = {
          id: conversationId,
          title: titleFromFirstMessage,
          messages: [],
        };

        conv = newConv;

        setConversations((prev) => [newConv, ...prev]);
        setActiveConversation(newConv);
      } else {
        conversationId = conv.id;
      }

      // 2. Build user message content (include attachments label if any)
      let userContent = trimmed;
      debugger;
      if (hasFiles) {
        const filesLabel = pendingFiles
          .map((f) => `📎 ${f.name}`)
          .join("\n");
        userContent = trimmed ? `${filesLabel}\n\n${trimmed}` : filesLabel;
      }

      const userMsg: Message = {
        id: Date.now() -1, // temporary ID
        role: "user",
        content: userContent || "",
      };

      let updated: Conversation = {
        ...conv,
        messages: [...conv.messages, userMsg],
      };

      setActiveConversation(updated);
      setConversations((prev) => {
        const filtered = prev.filter((c) => c.id !== updated.id);
        return [updated, ...filtered];
      });

      // 3. Call backend
      if (hasFiles) {
        const res = await uploadChat(conversationId, trimmed, pendingFiles);

        const aiMsg: Message = {
          id: res.message_id,
          role: "assistant",
          content: res.answer,
        };

        updated = {
          ...updated,
          messages: [...updated.messages, aiMsg],
        };

        setActiveConversation(updated);
        setConversations((prev) => {
          const filtered = prev.filter((c) => c.id !== updated.id);
          return [updated, ...filtered];
        });

        setTimeout(() => {
          bottomRef.current?.scrollIntoView({ behavior: "smooth" });
        }, 50);
      } else if (hasText) {
        const res = await sendChat(conversationId, trimmed);

        const aiMsg: Message = {
          id: res.message_id,
          role: "assistant",
          content: res.answer,
        };

        updated = {
          ...updated,
          messages: [...updated.messages, aiMsg],
        };

        setActiveConversation(updated);
        setConversations((prev) => {
          const filtered = prev.filter((c) => c.id !== updated.id);
          return [updated, ...filtered];
        });

        setTimeout(() => {
          bottomRef.current?.scrollIntoView({ behavior: "smooth" });
        }, 50);
      }
    } finally {
      setLoading(false);
      setPendingFiles([]);
    }
  }

  async function handleRename(conv: Conversation) {
    const newTitle = prompt("Enter new name:", conv.title ?? "");
    if (!newTitle || newTitle.trim() === "") return;

    const title = newTitle.trim();

    try {
      await renameConversation(conv.id, title);
    } catch (error) {
      console.error("Rename failed:", error);
      return;
    }

    const updatedConv = { ...conv, title };

    setConversations((prev) =>
      prev.map((c) => (c.id === conv.id ? updatedConv : c))
    );

    if (activeConversation?.id === conv.id) {
      setActiveConversation(updatedConv);
    }
  }

  async function handleDelete(convId: number) {
    if (!confirm("Delete this conversation?")) return;

    try {
      await deleteConversation(convId);
    } catch (err) {
      console.error("Delete failed:", err);
    }

    setConversations((prev) => {
      const updated = prev.filter((c) => c.id !== convId);

      if (activeConversation?.id === convId) {
        if (updated.length > 0) {
          setActiveConversation(updated[0]);
        } else {
          setActiveConversation({
            id: TEMP_CONVERSATION_ID,
            title: null,
            messages: [],
          });
        }
      }

      return updated;
    });
  }

  async function handleAddToNotesAndDelete() {
    if (!deleteTarget) return;

    // Add to notes
    await handleAddMessageToNotes(deleteTarget.content);

    // Delete the message
    await deleteMessage(deleteTarget.id);

    // update UI
    setActiveConversation(prev =>
      prev
        ? { ...prev, messages: prev.messages.filter((_, i) => i !== deleteTarget.index) }
        : prev
    );

    setShowDeleteModal(false);
  }

  async function handleFinalDelete() {
    if (!deleteTarget) return;

    await deleteMessage(deleteTarget.id);

    // update UI
    setActiveConversation(prev =>
      prev
        ? { ...prev, messages: prev.messages.filter((_, i) => i !== deleteTarget.index) }
        : prev
    );

    setShowDeleteModal(false);
  }

  function handleAddToNotes(conv: Conversation) {
    alert("Add to Notes feature coming soon!");
  }

  async function handleAddMessageToNotes(content: string) {
    try {
      const res = await addMessageToNoteAPI(user.id, content, "Chat Snippet");

      // Load the newly created note
      const fresh = await getNote(res.id);

      setNotes((prev) => [fresh, ...prev]);

    } catch (err) {
      console.error("Error adding message to notes:", err);
    }
  }

  function handleMessagesScroll(e: React.UIEvent<HTMLDivElement>) {
    const target = e.currentTarget;

    // If the user scrolled close to the top, load older messages
    if (target.scrollTop < 120 && activeConversation) {
      loadMessages(activeConversation.id, true);
    }
  }

  async function handleDeleteMessage(messageId: number, index: number) {
    if (!activeConversation) return;

    try {
      await deleteMessage(messageId);
    } catch (err) {
      console.error("Delete message failed:", err);
    }

    const updatedMessages = activeConversation.messages.filter(
      (_, i) => i !== index
    );

    setActiveConversation({
      ...activeConversation,
      messages: updatedMessages,
    });
  }

  function openDeleteModal(id: number, content: string, index: number) {
    setDeleteTarget({ id, content, index });
    setShowDeleteModal(true);
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleChatFileUpload(
    e: React.ChangeEvent<HTMLInputElement>
  ) {
    const files = e.target.files ? Array.from(e.target.files) : [];
    if (!files.length) return;
    setPendingFiles((prev) => [...prev, ...files]);
    // reset input so same file can be selected again
    e.target.value = "";
  }

  function handleLogout() {
    localStorage.removeItem("user");
    saveUser(null); // optional if your helper expects it
    window.location.reload(); // simplest reset
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

    {/* GLOBAL FLOATING MENU FOR NOTES & CONVERSATIONS */}
    {activeNoteMenuData && (
      <div
        className="absolute z-[9999]"
        style={{
          top: activeNoteMenuData.top,
          left: activeNoteMenuData.left,
          width: 160,
        }}
      >
        {activeNoteMenuData.type === "note" && (
          <div className="bg-[#1E1E1E] border border-[#333] rounded-lg shadow-xl">
            <button
              onClick={() => handleEditNote(activeNoteMenuData.item)}
              className="w-full text-left px-4 py-2 hover:bg-[#333] text-white"
            >
              Edit
            </button>

            <button
              onClick={() => handleDeleteNote(activeNoteMenuData.item.id)}
              className="w-full text-left px-4 py-2 hover:bg-[#422] text-red-400"
            >
              Delete
            </button>
          </div>
        )}

        {activeNoteMenuData.type === "conversation" && (
          <div className="bg-[#1E1E1E] border border-[#333] rounded-lg shadow-xl">
            <button
              onClick={() => handleRename(activeNoteMenuData.item)}
              className="w-full text-left px-4 py-2 hover:bg-[#333] text-white"
            >
              Rename
            </button>

            <button
              onClick={() => handleAddToNotes(activeNoteMenuData.item)}
              className="w-full text-left px-4 py-2 hover:bg-[#333] text-white"
            >
              Add to Notes
            </button>

            <button
              onClick={() => handleDelete(activeNoteMenuData.item.id)}
              className="w-full text-left px-4 py-2 hover:bg-[#422] text-red-400"
            >
              Delete
            </button>
          </div>
        )}
      </div>
    )}

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
          <div className="border-b border-[#2A2A2A] relative">
            <button
              onClick={() => setShowNotes(!showNotes)}
              className="w-full px-4 py-3 flex justify-between items-center bg-[#2A2C2F] text-[#E5E7EB] text-sm hover:bg-[#2A2C2F] transition"
            >
              <span>Notes</span>
              <span className="text-gray-400">{showNotes ? "▾" : "▸"}</span>
            </button>

            {showNotes && (
              <div className="px-4 py-2 max-h-56 overflow-y-auto space-y-2 relative">
                
                {notes.length === 0 && (
                  <p className="text-xs text-gray-500">No notes found</p>
                )}

                {/* NEW NOTE BUTTON */}
                <button
                  onClick={handleNewNote}
                  className="w-full bg-blue-300 text-blue-900 rounded-full text-sm font-medium hover:bg-blue-400 transition shadow-sm"
                >
                  + New Note
                </button>

                {notes.map((note) => (
                  <div key={note.id} className="relative">
                    <div
                      className="rounded cursor-pointer flex justify-between items-center"
                      onClick={() => openNoteEditor(note)}
                    >
                      <span className="truncate">{note.title || "Untitled"}</span>

                      {/* 3-dot button */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          const rect = e.currentTarget.getBoundingClientRect();

                          setActiveNoteMenuData({
                            type: "note",
                            item: note,
                            top: rect.top + 24, // menu below button
                            left: rect.right - 160 // align right side
                          });
                        }}
                        className="text-gray-400 hover:text-white px-2 text-xl"
                      >
                        ⋯
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>


          {/* Messages Section */}
          <div className="flex-1 flex flex-col overflow-hidden relative">
            <button
              onClick={() => setShowConversations(!showConversations)}
              className="w-full px-4 py-3 flex justify-between items-center bg-[#2A2C2F] text-[#E5E7EB] text-sm border-b border-[#2C2D2F]"
            >
              <span className="font-medium">Messages</span>
              <span className="text-gray-400">
                {showConversations ? "▾" : "▸"}
              </span>
            </button>

            {showConversations && (
              <div className="flex-1 overflow-y-auto p-3 space-y-2 relative">
                
                <button
                  onClick={handleNewConversation}
                  className="w-full bg-green-300 text-green-900 rounded-full text-sm font-medium hover:bg-green-400 transition shadow-sm"
                >
                  + New Chat
                </button>

                {conversations.map((conv) => (
                  <div key={conv.id} className="relative">
                    <div
                      onClick={async () => {
                        setActiveConversation(conv);

                        // Load last page of messages
                        await loadMessages(conv.id, false);

                        // ⭐ Scroll AFTER React finishes updating the DOM
                        requestAnimationFrame(() => {
                          requestAnimationFrame(() => {
                            bottomRef.current?.scrollIntoView({ behavior: "auto" });
                          });
                        });
                      }}
                      className={`
                        rounded cursor-pointer transition flex justify-between items-center
                        ${
                          activeConversation?.id === conv.id
                            ? "bg-[#2A2C2F] text-white shadow-sm"
                            : "bg-[#1E1F22] text-gray-400 hover:bg-[#2A2C2F] hover:text-white shadow-sm"
                        }
                      `}
                    >
                      <span className="flex-1 truncate">
                        {conv.title || `Conversation ${conv.id}`}
                      </span>
                      {/* 3-dot button for converstation*/}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          const rect = e.currentTarget.getBoundingClientRect();

                          setActiveNoteMenuData({
                            type: "conversation",
                            item: conv,
                            top: rect.top + 24,
                            left: rect.right - 160
                          });
                        }}
                        className="text-gray-400 hover:text-white px-2 text-xl"
                      >
                        ⋯
                      </button>
                    </div>

                  </div>
                ))}
              </div>
            )}
          </div>

        </aside>
      )}

      {/* RIGHT SIDE: HEADER + CONTENT + FOOTER */}
      <div
        className="flex-1 flex flex-col h-full"
        ref={layoutRef}
      >
        {/* HEADER */}
      <header className="h-10 flex items-center justify-between px-6 bg-[#202123] border-b border-[#2C2D2F] shadow-md">
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-300 opacity-80">
            {activeConversation.title || "Conversation"}
          </span>
        </div>

        {/* LOGOUT BUTTON */}
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <span>Logged in as {user.email}</span>

          <button
            onClick={handleLogout}
            className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white rounded-full text-xs"
          >
            Logout
          </button>
        </div>
      </header>
        
        {/* CENTER: MESSAGES + NOTE PANEL */}
        <main className="flex-1 px-5 py-10 overflow-hidden">
          <div className="h-full flex gap-4">
            {/* Messages column */}
            <div
              ref={messagesContainerRef}   // ⭐ REQUIRED
              className="flex-1 min-w-0 overflow-y-auto"
              onScroll={handleMessagesScroll}
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDropFile}
            >
              <div className="max-w-[740px] mx-auto flex flex-col gap-4">
                {activeConversation.messages.map((msg, idx) => (
                  <ChatBubble
                    key={idx}
                    role={msg.role}
                    content={msg.content}
                    onAdd={() => handleAddMessageToNotes(msg.content)}
                    onDelete={() => openDeleteModal(msg.id, msg.content, idx)}
                  />
                ))}

                {loading && (
                  <ChatBubble role="assistant" content="⏳ Thinking..." />
                )}

                <div ref={bottomRef} />
              </div>
            </div>

            {/* Resizer + Note panel */}
            {selectedNote && (
              <>
                {/* Resizer bar */}
                <div
                  className="w-[5px] cursor-col-resize bg-[#374151] rounded-full self-stretch"
                  onMouseDown={startNotePanelResize}
                />

                {/* Note editor panel */}
                <div
                  className="flex flex-col bg-[#111827] border border-[#374151] rounded-2xl p-4 overflow-hidden"
                  style={{ width: notePanelWidth }}
                >
                  {/* Note title */}
                  <input
                    value={noteTitleDraft}
                    onChange={(e) => {
                      setNoteTitleDraft(e.target.value);
                    }}
                    placeholder="Note title..."
                    className="w-full bg-transparent border-b border-[#374151] pb-2 mb-4 text-sm text-blue-100 focus:outline-none focus:border-blue-500"
                  />

                  {/* Note content */}
                  <textarea
                    value={noteContentDraft}
                    onChange={(e) => {
                      setNoteContentDraft(e.target.value);
                    }}
                    className="flex-1 w-full bg-transparent text-sm text-gray-100 resize-none focus:outline-none rounded-md p-2 border border-[#374151]"
                    placeholder="Write your note here..."
                  />

                  {/* Footer buttons */}
                  <div className="mt-4 flex justify-between items-center">
                    <span className="text-xs text-gray-500">
                      {isNoteDirty ? "Unsaved changes" : "Up to date"}
                    </span>
                    <div className="flex gap-2">
                      <button
                        onClick={handleDiscardNoteChanges}
                        disabled={!isNoteDirty}
                        className="px-3 py-1 rounded-full text-xs border border-[#4B5563] text-gray-300 disabled:opacity-40"
                      >
                        Discard
                      </button>
                      <button
                        onClick={handleSaveNote}
                        disabled={!isNoteDirty}
                        className="px-4 py-1 rounded-full text-xs bg-blue-600 hover:bg-blue-500 text-white disabled:bg-gray-700 disabled:cursor-not-allowed"
                      >
                        Save
                      </button>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </main>

        {/* FOOTER / INPUT BAR */}
        <footer className="border-t border-[#2C2D2F] bg-[transparent] p-6">
          <div
            className="max-w-[740px] mx-auto flex w-full flex-col gap-2"
          >
            {/* ATTACHMENT CHIPS (above input, ChatGPT-style) */}
            {pendingFiles.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-1">
                {pendingFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 bg-[#111827] border border-[#374151] rounded-2xl px-2 py-1 max-w-[260px]"
                  >
                    {file.type.startsWith("image/") ? (
                      <img
                        src={URL.createObjectURL(file)}
                        alt={file.name}
                        className="w-8 h-8 rounded object-cover"
                      />
                    ) : (
                      <span className="text-sm">📎</span>
                    )}
                    <div className="flex flex-col min-w-0">
                      <span className="text-xs text-gray-100 truncate">
                        {file.name}
                      </span>
                      <span className="text-[10px] text-gray-400">
                        {Math.round(file.size / 1024)} KB
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() =>
                        setPendingFiles((prev) => prev.filter((_, i) => i !== index))
                      }
                      className="ml-1 text-[10px] text-gray-400 hover:text-red-300"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* INPUT BUBBLE CONTAINER */}
            <div
              className="flex-1 bg-[#1E1E1E] rounded-3xl px-4 py-2 flex items-end shadow-md relative"
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDropFile}
            >
              <input type="file" multiple hidden ref={attachmentInputRef} onChange={handleChatFileUpload} />
              <button
                onClick={() => attachmentInputRef.current?.click()}
                className="w-8 h-8 rounded-full bg-[#555] flex items-center justify-center absolute left-3 bottom-3"
              >
                +
              </button>

              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  autoResize();
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                    return;
                  }
                  autoResize();
                }}
                rows={1}
                placeholder="Message RecallAI..."
                style={{
                  flex: 1,
                  width: "100%",
                  background: "transparent",
                  resize: "none",
                  border: "none",
                  outline: "none",
                  color: "white",
                  fontSize: "16px",
                  lineHeight: "1.5",
                  paddingLeft: "48px",
                  paddingRight: "42px",
                  paddingTop: "12px",
                  paddingBottom: "12px",
                  maxHeight: "200px",
                  overflow: "hidden",
                }}
              />

              {/* SEND ICON INSIDE TEXTAREA BUBBLE */}
              <button
                onClick={handleSend}
                disabled={loading || (!input.trim() && pendingFiles.length === 0)}
                style={{
                  position: "absolute",
                  right: "14px",
                  bottom: "14px",
                  width: "32px",
                  height: "32px",
                  borderRadius: "50%",
                  border: "none",
                  background: input.trim() || pendingFiles.length > 0 ? "#3B82F6" : "#444",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: input.trim() ? "pointer" : "not-allowed",
                  opacity: loading ? 0.6 : 1,
                }}
              >
                <svg
                  style={{
                    width: "18px",
                    height: "18px",
                    fill: "white",
                  }}
                  viewBox="0 0 24 24"
                >
                  <path d="M2 21l21-9L2 3v7l15 2-15 2v7z" />
                </svg>
              </button>
            </div>
          </div>
        </footer>
      </div>
      {showDeleteModal && deleteTarget && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-[#1f1f1f] p-5 rounded-xl w-80 shadow-xl text-white">
            <h3 className="text-lg font-semibold mb-3">Delete Message</h3>

            <p className="text-sm mb-4 text-gray-300">
              What would you like to do with this message?
            </p>

            <div className="space-y-3">

              {/* Add to Notes & Delete */}
              <button
                className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded-lg"
                onClick={() => handleAddToNotesAndDelete()}
              >
                📒 Add to Notes & Delete
              </button>

              {/* Delete Only */}
              <button
                className="w-full bg-red-600 hover:bg-red-700 py-2 rounded-lg"
                onClick={() => handleFinalDelete()}
              >
                🗑 Delete Only
              </button>

              {/* Cancel */}
              <button
                className="w-full bg-gray-600 hover:bg-gray-700 py-2 rounded-lg"
                onClick={() => setShowDeleteModal(false)}
              >
                Cancel
              </button>

            </div>
          </div>
        </div>
      )}
    </div>
  );
}
