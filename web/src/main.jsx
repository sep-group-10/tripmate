import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./index.css";
import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import { TourismDataProvider } from "./context/TourismDataContext.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <TourismDataProvider>
          <App />
        </TourismDataProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);
