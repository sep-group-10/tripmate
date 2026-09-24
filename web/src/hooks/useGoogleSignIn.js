import { useEffect } from "react";

const GSI_SCRIPT_SRC = "https://accounts.google.com/gsi/client";

function loadGoogleScript() {
  return new Promise((resolve, reject) => {
    if (window.google?.accounts?.id) {
      resolve();
      return;
    }
    const existing = document.querySelector(`script[src="${GSI_SCRIPT_SRC}"]`);
    if (existing) {
      existing.addEventListener("load", () => resolve());
      existing.addEventListener("error", reject);
      return;
    }
    const script = document.createElement("script");
    script.src = GSI_SCRIPT_SRC;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

// Renders Google's own Sign In button into containerRef - a custom
// button can't trigger this flow directly, Google requires its own
// rendered button or an explicit prompt() call.
export function useGoogleSignIn(containerRef, onCredential) {
  useEffect(() => {
    let cancelled = false;

    loadGoogleScript().then(() => {
      if (cancelled || !containerRef.current) return;
      window.google.accounts.id.initialize({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
        callback: (response) => onCredential(response.credential),
      });
      window.google.accounts.id.renderButton(containerRef.current, {
        theme: "outline",
        size: "large",
        width: 336,
      });
    });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}
