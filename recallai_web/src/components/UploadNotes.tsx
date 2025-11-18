import { useState } from "react";
import { uploadNotes } from "../api/chatApi";
import { getUser } from "../utils/auth";

export function UploadNotes() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    if (!e.target.files) return;

    const user = getUser();
    if (!user) {
      setStatus("Not logged in.");
      return;
    }

    setLoading(true);
    setStatus("");

    const files = Array.from(e.target.files);

    try {
      // Correct form: /notes/bulk?user_id=${user.id}
      await uploadNotes(files, user.id);

      setStatus("Notes uploaded successfully!");
    } catch (err: any) {
      console.error("Upload error:", err);

      // Show backend error detail if exists
      if (err.response && err.response.data && err.response.data.detail) {
        setStatus("Upload failed: " + JSON.stringify(err.response.data.detail));
      } else {
        setStatus("Upload failed (check console).");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="border p-4 rounded-lg shadow bg-gray-900 text-gray-200">
      <label className="font-bold">Upload Notes</label>

      <input
        type="file"
        multiple
        onChange={handleUpload}
        className="block mt-2"
      />

      {loading && (
        <div className="text-sm text-blue-400 mt-2">Uploading...</div>
      )}

      {!loading && status && (
        <div className="text-sm text-gray-300 mt-2">{status}</div>
      )}
    </div>
  );
}
