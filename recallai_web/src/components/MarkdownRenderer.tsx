import React, { useEffect } from "react";
import { marked } from "marked";
import hljs from "highlight.js";
import "highlight.js/styles/github-dark.css";

interface Props {
  children: string;
  className?: string;
}

export default function MarkdownRenderer({ children, className }: Props) {
  const safeText =
    typeof children === "string" ? children : String(children || "");

  // Custom code renderer with syntax highlight + copy button
  const renderer = {
    code(codeObj: any) {
      const { text, lang } = codeObj;

      const language =
        lang && hljs.getLanguage(lang) ? lang : "plaintext";

      const highlighted = hljs.highlight(text, { language }).value;

      return `
        <div class="code-block-wrapper">
          <button class="code-copy-btn" data-code="${encodeURIComponent(
            text
          )}">
            Copy
          </button>
          <pre><code class="hljs ${language}">${highlighted}</code></pre>
        </div>
      `;
    },
  };

  // Register renderer
  marked.use({ renderer });

  // Convert markdown → HTML
  const html = marked.parse(safeText);

  // Attach copy button events
  useEffect(() => {
    const buttons = document.querySelectorAll(".code-copy-btn");

    const handler = (e: any) => {
      const encoded = e.target.getAttribute("data-code");
      if (!encoded) return;
      const decoded = decodeURIComponent(encoded);

      navigator.clipboard.writeText(decoded);

      // Feedback
      const original = e.target.innerText;
      e.target.innerText = "Copied!";
      setTimeout(() => (e.target.innerText = original), 1200);
    };

    buttons.forEach((btn) => btn.addEventListener("click", handler));

    // Cleanup
    return () => {
      buttons.forEach((btn) => btn.removeEventListener("click", handler));
    };
  }, [html]);

  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
