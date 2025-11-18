import React, { useState, useRef } from "react";
import { uploadNotes } from "../api/chatApi";
import { getUser } from "../utils/auth";

interface UploadNotesProps {
  // Treat setNotes like a React state setter
  setNotes?: React.Dispatch<React.SetStateAction<any[]>>;
}

export function UploadNotes({ setNotes }: UploadNotesProps) {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Handle file selection (manual browse)
  async function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    if (!e.target.files) return;
    await processFiles(Array.from(e.target.files));
  }

  // Handle drag & drop upload
  async function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    if (!e.dataTransfer.files) return;
    await processFiles(Array.from(e.dataTransfer.files));
  }

  async function processFiles(files: File[]) {
    const user = getUser();
    if (!user) {
      setStatus("Not logged in.");
      return;
    }

    setLoading(true);
    setStatus("");

    try {
      await uploadNotes(files, user.id);
      setStatus("Notes uploaded successfully!");

      // Update notes list in parent (if provided)
      if (setNotes) {
        const uploaded = files.map((f) => ({
          id: f.name,
          title: f.name,
          filename: f.name,
        }));

        // ✅ Correct functional update
        setNotes((prev) => [...prev, ...uploaded]);
      }
    } catch (err: any) {
      console.error("Upload error:", err);
      if (err.response?.data?.detail) {
        setStatus("Upload failed: " + JSON.stringify(err.response.data.detail));
      } else {
        setStatus("Upload failed.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-2">
      {/* HEADER LABEL */}
      {/* DRAG & DROP ZONE */}
      <div
        className="
          border border-[#3A3A3A]
          bg-[#1E1E1E]
          rounded-lg p-5 text-center
          cursor-pointer
          hover:bg-[#2A2A2A]
          transition
        "
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        <p className="text-gray-300 font-semibold">Notes</p>
        <p className="text-gray-300 font-semibold">Drag & Drop Files</p>
        <p className="text-xs text-gray-500 mt-1">or click to browse</p>
      </div>

      {/* Hidden file input */}
      <input
        type="file" 
        multiple
        hidden
        ref={fileInputRef}
        onChange={handleFileSelect}
      />

      {/* Status Message */}
      {loading && <div className="text-xs text-blue-400">Uploading...</div>}
      {!loading && status && (
        <div className="text-xs text-gray-400">{status}</div>
      )}
    </div>
  );
}
