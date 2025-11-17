import { useState } from "react";
import { uploadNotes } from "../api/chatApi";

export function UploadNotes() {
  const [loading, setLoading] = useState(false);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    if (!e.target.files) return;

    setLoading(true);
    const files = Array.from(e.target.files);
    await uploadNotes(files);
    setLoading(false);

    alert("Notes uploaded successfully!");
  }

  return (
    <div className="border p-4 rounded-lg shadow">
      <label className="font-bold">Upload Notes</label>
      <input
        type="file"
        multiple
        onChange={handleUpload}
        className="block mt-2"
      />
      {loading && <div className="text-sm text-gray-500">Uploading...</div>}
    </div>
  );
}
