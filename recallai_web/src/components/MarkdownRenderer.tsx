import React, { useEffect } from "react";
import { marked } from "marked";
import hljs from "highlight.js";
import "highlight.js/styles/github-dark.css";
import katex from "katex";
import "katex/dist/katex.min.css";

interface Props {
  children: string;
  className?: string;
}

// Helper: render LaTeX math ($...$, $$...$$, \(...\), \[...\])
function renderMath(source: string): string {
  let text = source;

  // Block math: $$ ... $$
  text = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, expr) => {
    const html = katex.renderToString(expr, {
      displayMode: true,
      throwOnError: false,
    });
    return `<div class="math-block">${html}</div>`;
  });

  // Inline math: $ ... $
  text = text.replace(/(?<!\$)\$([^\$]+?)\$(?!\$)/g, (_, expr) => {
    const html = katex.renderToString(expr, {
      displayMode: false,
      throwOnError: false,
    });
    return `<span class="math-inline">${html}</span>`;
  });

  // Inline math: \( ... \)
  text = text.replace(/\\\(([\s\S]+?)\\\)/g, (_, expr) => {
    const html = katex.renderToString(expr, {
      displayMode: false,
      throwOnError: false,
    });
    return `<span class="math-inline">${html}</span>`;
  });

  // Block math: \[ ... \]
  text = text.replace(/\\\[([\s\S]+?)\\\]/g, (_, expr) => {
    const html = katex.renderToString(expr, {
      displayMode: true,
      throwOnError: false,
    });
    return `<div class="math-block">${html}</div>`;
  });

  return text;
}

export default function MarkdownRenderer({ children, className }: Props) {
  const safeText =
    typeof children === "string" ? children : String(children || "");

  // 1) First render LaTeX to HTML
  const withMath = renderMath(safeText);

  // 2) Create a renderer and override code blocks (your copy+HLJS logic)
  const renderer: any = new marked.Renderer();

  renderer.code = function (...args: any[]) {
    let code = "";
    let lang = "";

    // Marked v7+ style: (code, lang)
    if (typeof args[0] === "string") {
      code = args[0];
      lang = args[1] || "";
    }
    // Older style: ({ text, lang })
    else if (typeof args[0] === "object" && args[0] !== null) {
      code = args[0].text || "";
      lang = args[0].lang || "";
    } else {
      code = String(args[0] ?? "");
    }

    const language = lang && hljs.getLanguage(lang) ? lang : "plaintext";
    const highlighted = hljs.highlight(code, { language }).value;

    return `
      <div class="code-block-wrapper">
        <button class="code-copy-btn" data-code="${encodeURIComponent(code)}">
          Copy
        </button>
        <pre><code class="hljs ${language}">${highlighted}</code></pre>
      </div>
    `;
  };

  // 3) Apply renderer + markdown options
  marked.setOptions({
    renderer,
    gfm: true,
    breaks: true,
  });

  // 4) Convert markdown → HTML (math is already embedded as HTML)
  const html = marked.parse(withMath);

  // 5) Wire up "Copy" buttons in code blocks
  useEffect(() => {
    const buttons = document.querySelectorAll(".code-copy-btn");

    const handler = (e: any) => {
      const encoded = e.target.getAttribute("data-code");
      if (!encoded) return;

      const decoded = decodeURIComponent(encoded);
      navigator.clipboard.writeText(decoded);

      const original = e.target.innerText;
      e.target.innerText = "Copied!";
      setTimeout(() => (e.target.innerText = original), 1200);
    };

    buttons.forEach((btn) => btn.addEventListener("click", handler));
    return () => {
      buttons.forEach((btn) => btn.removeEventListener("click", handler));
    };
  }, [html]);

  return (
    <div
      className={`markdown-body ${className || ""}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
