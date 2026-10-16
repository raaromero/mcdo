import { defineConfig } from "vite";

// Relative base so the build works at a domain root (Vercel) and under /<repo>/ (GitHub Pages).
export default defineConfig({ base: "./" });
