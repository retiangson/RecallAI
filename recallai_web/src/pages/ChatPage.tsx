import { ChatWindow } from "../components/ChatWindow";
import { UploadNotes } from "../components/UploadNotes";

export function ChatPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <UploadNotes />
      <ChatWindow />
    </div>
  );
}

