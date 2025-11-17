export function ChatBubble({ role, content }: { role: string; content: string }) {
  const isUser = role === "user";

  return (
    <div
      className={`p-3 rounded-lg max-w-[80%] ${
        isUser ? "bg-blue-200 ml-auto" : "bg-gray-200 mr-auto"
      }`}
    >
      {content}
    </div>
  );
}
