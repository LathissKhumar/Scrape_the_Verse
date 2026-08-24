import { type ReactNode } from "react";

export function ComicPanel({
  children,
  className = "",
  glowing = false,
}: {
  children: ReactNode;
  className?: string;
  glowing?: boolean;
}) {
  return (
    <div
      className={`glass-level-2 p-6 md:p-8 transition-all duration-300 ${
        glowing
          ? "border-violet-accent/40 shadow-violet-accent/10 shadow-2xl"
          : ""
      } ${className}`}
    >
      {children}
    </div>
  );
}
