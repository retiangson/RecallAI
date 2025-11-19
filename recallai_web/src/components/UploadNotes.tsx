import React, { useState, useRef } from "react";
import { uploadNotes } from "../api/chatApi";
import { getUser } from "../utils/auth";

interface UploadNotesProps {
  setNotes?: React.Dispatch<React.SetStateAction<any[]>>;
}

export function UploadNotes({ setNotes }: UploadNotesProps) {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // ---------------------------------------------
  // Handle manual file selection
  // ---------------------------------------------
  async function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    if (!e.target.files) return;
    const files = Array.from(e.target.files);

    setSelectedFiles((prev) => [...prev, ...files]); // show list
    await processFiles(files);
  }

  // ---------------------------------------------
  // Drag & Drop
  // ---------------------------------------------
  async function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    if (!e.dataTransfer.files) return;
    const files = Array.from(e.dataTransfer.files);

    setSelectedFiles((prev) => [...prev, ...files]); // show list
    await processFiles(files);
  }

  // ---------------------------------------------
  // Upload Files → Backend → Save Notes
  // ---------------------------------------------
  async function processFiles(files: File[]) {
    const user = getUser();
    if (!user) {
      setStatus("Not logged in.");
      return;
    }

    setLoading(true);
    setStatus("Processing files...");

    try {
      const uploadedNotes = await uploadNotes(files, user.id);

      setStatus("Notes imported successfully!");

      // Notify parent to update UI
      if (setNotes && uploadedNotes) {
        setNotes((prev) => [...uploadedNotes, ...prev]);
      }
    } catch (err: any) {
      console.error("Upload error:", err);
      setStatus("Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-3">
      {/* ---- DRAG AND DROP ZONE ---- */}
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
        <p className="text-gray-300 font-semibold">Upload Notes</p>
        <p className="text-gray-400">Drag & Drop files here</p>
        <p className="text-xs text-gray-500 mt-1">or click to browse</p>
      </div>

      {/* Hidden Input */}
      <input
        type="file"
        multiple
        hidden
        accept="*/*"
        ref={fileInputRef}
        onChange={handleFileSelect}
      />

      {/* ---- FILE LIST ---- */}
      {selectedFiles.length > 0 && (
        <div className="max-h-28 overflow-y-auto border border-[#343434] rounded-lg p-2">
          <p className="text-xs text-gray-400 mb-1">Files to upload:</p>
          {selectedFiles.map((file, i) => (
            <div
              key={i}
              className="text-xs text-gray-300 bg-[#222] rounded px-2 py-1 mb-1 truncate"
            >
              {file.name}
            </div>
          ))}
        </div>
      )}

      {/* ---- STATUS AREA ---- */}
      {loading && (
        <div className="text-xs text-blue-400 animate-pulse">
          Importing notes, please wait...
        </div>
      )}

      {!loading && status && (
        <div className="text-xs text-gray-400">{status}</div>
      )}
    </div>
  );
}
