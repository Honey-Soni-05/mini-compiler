import type { CompileResult } from "../types/compiler";

const API_BASE = window.location.hostname === "localhost" 
  ? "/api" 
  : "https://mini-compiler-backend.onrender.com/api";

export async function compileCode(code: string): Promise<CompileResult> {
  const response = await fetch(`${API_BASE}/compile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Server error ${response.status}: ${text}`);
  }

  return response.json() as Promise<CompileResult>;
}
