import App from "@/App.tsx"
import AudioConverter from "@/components/audio-converter"
import BaseLayout from "@/components/base-layout"
import ErrorPage from "@/components/error-page"
import Settings from "@/components/settings.tsx"
import "@/index.css"
import { createRoot } from "react-dom/client"
import { BrowserRouter, Route, Routes } from "react-router"

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <Routes>
      <Route element={<BaseLayout />}>
        <Route index element={<App />} />
        <Route path="convert" element={<AudioConverter />} />
        <Route path="settings" element={<Settings />} />
        <Route path="*" element={<ErrorPage />} />
      </Route>
    </Routes>
  </BrowserRouter>,
)
