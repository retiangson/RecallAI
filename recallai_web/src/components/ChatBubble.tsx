import React from "react";
import MarkdownRenderer from "./MarkdownRenderer";
import "highlight.js/styles/github-dark.css";
import "../styles/markdown.css";

interface Props {
  role: "user" | "assistant";
  content: any;
}

export default function ChatBubble({ role, content }: Props) {
  const isUser = role === "user";

  return (
    <div
      className={`w-full flex ${
        isUser ? "justify-end" : "justify-start"
      } my-5`}   // ← added more spacing
    >
      <div
        className={`
          max-w-[740px] px-5 py-4 
          rounded-2xl text-[16px] leading-relaxed
          ${
            isUser
              ? "bg-[#2F2F2F] text-gray-100" // USER
              : "bg-blue-600 text-white" // ASSISTANT
          }
        `}
        style={{
          borderRadius: "10px", // ← restored smooth bubble curve
          padding: "15px 20px", // ← adjusted padding for better readability
          
        }}
      >
        <MarkdownRenderer>{content}</MarkdownRenderer>
      </div>
    </div>
  );
}
