import App from "@/App.tsx";
import Settings from "@/components/settings.tsx";
import "@/index.css";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router";
import BaseLayout from "@/components/base-layout";
import ErrorPage from "@/components/error-page";

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <Routes>
      <Route element={<BaseLayout />}>
        <Route index element={<App />} />
        <Route path="settings" element={<Settings />} />
        <Route path="*" element={<ErrorPage />} />
      </Route>
    </Routes>
  </BrowserRouter>,
);
