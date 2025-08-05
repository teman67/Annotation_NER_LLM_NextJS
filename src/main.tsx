import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import App from "./App.tsx";

// Immediately indicate that styles are loading
document.documentElement.classList.add("app-loading");

// Remove loading state after a minimal delay to ensure CSS is processed
requestAnimationFrame(() => {
  requestAnimationFrame(() => {
    document.documentElement.classList.add("app-loaded");
    document.documentElement.classList.remove("app-loading");
  });
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
