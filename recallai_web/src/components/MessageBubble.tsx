import React from "react";
import clsx from "clsx";

interface Props {
  role: "user" | "assistant";
  content: string;
}

export function MessageBubble({ role, content }: Props) {
  return (
    <div
      className={clsx(
        "p-3 my-2 rounded-lg max-w-[75%]",
        role === "user"
          ? "bg-blue-500 text-white self-end"
          : "bg-gray-200 text-black self-start"
      )}
    >
      {content}
    </div>
  );
}
