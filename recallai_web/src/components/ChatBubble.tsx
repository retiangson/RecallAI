import React, { useState } from "react";
import { marked } from "marked";
import MarkdownRenderer from "./MarkdownRenderer";
import "highlight.js/styles/github-dark.css";
import "../styles/markdown.css";

interface Props {
  role: "user" | "assistant";
  content: any;
}

export default function ChatBubble({ role, content }: Props) {
  const isUser = role === "user";
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const html: string = await marked.parse(
      typeof content === "string" ? content : ""
    );

    const plain = typeof content === "string" ? content : "";

    const item = new ClipboardItem({
      "text/html": new Blob([html], { type: "text/html" }),
      "text/plain": new Blob([plain], { type: "text/plain" }),
    });

    await navigator.clipboard.write([item]);

    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div
      className={`w-full flex ${
        isUser ? "justify-end" : "justify-start"
      } my-[3px]`} // 🔥 reduced gap to ~3px
    >
      <div
        className={`
          relative max-w-[740px] px-5 py-4 
          rounded-2xl text-[16px] leading-relaxed
          ${
            isUser
              ? "bg-[#2F2F2F]/80 text-gray-100"
              : "text-white"
          }
          backdrop-blur-sm
          shadow-sm
        `}
      >
        <MarkdownRenderer>{content}</MarkdownRenderer>

        {/* COPY BUTTON (assistant only, bottom-left) */}
        {!isUser && (
          <button
            onClick={handleCopy}
            className="
              absolute -bottom-6 left-3 
              flex items-center gap-1 
              text-xs opacity-60 hover:opacity-100 transition
              px-2 py-1 
              bg-[#2A2A2A]/60 backdrop-blur-sm
              rounded-md
            "
          >
            {/* Copy Icon */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="14"
              height="14"
              fill="currentColor"
              viewBox="0 0 16 16"
            >
              <path d="M10 1.5A1.5 1.5 0 0 1 11.5 3v8A1.5 1.5 0 0 1 10 12.5H4A1.5 1.5 0 0 1 2.5 11V3A1.5 1.5 0 0 1 4 1.5h6Zm-6 1A.5.5 0 0 0 3.5 3v8a.5.5 0 0 0 .5.5h6a.5.5 0 0 0 .5-.5V3a.5.5 0 0 0-.5-.5H4Zm9 1.5v7.528a2.5 2.5 0 0 1-2 2.45V13h1a1.5 1.5 0 0 0 1.5-1.5V4h-.5Z" />
            </svg>

            {copied ? "Copied!" : "Copy"}
          </button>
        )}
      </div>
    </div>
  );
}
