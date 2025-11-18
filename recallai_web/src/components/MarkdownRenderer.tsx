import React from "react";
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

  // Custom code renderer – correct signature for Marked v5+
  const renderer = {
    code(codeObj: any) {
      const { text, lang } = codeObj;

      const language =
        lang && hljs.getLanguage(lang) ? lang : "plaintext";

      const highlighted = hljs.highlight(text, {
        language,
      }).value;

      return `<pre><code class="hljs ${language}">${highlighted}</code></pre>`;
    },
  };

  // Attach renderer
  marked.use({ renderer });

  // Convert markdown → HTML
  const html = marked.parse(safeText);

  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
