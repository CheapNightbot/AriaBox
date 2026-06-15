import { Button } from "@/components/ui/button";
import { ArrowLeftIcon, SettingsIcon } from "lucide-react";
import { NavLink, useLocation, useNavigate } from "react-router";
import "./header.css";

function Header() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <header className="text-center flex items-center justify-center w-[clamp(400px,90vw,1200px)] py-4 mb-2 relative">
      {location.pathname !== "/" && (
        <Button
          size="sm"
          className="absolute left-0 animate-in fade-in duration-500 ease-in-out slide-in-from-right-20"
          onClick={() => void navigate("/")}
        >
          <ArrowLeftIcon /> Back Home
        </Button>
      )}

      <h1
        id="header-logo"
        className="flex-1 select-none text-3xl font-semibold tracking-wide hover:cursor-pointer animate-in fade-in blur-in-sm duration-500 ease-in-out"
        onClick={() => (window.location.href = "/")}
      >
        AriaBox ⨾<span className="rotate">💿</span>✮˚.⋆
      </h1>

      <NavLink
        to="/settings"
        className={({ isActive }) => (isActive ? "bg-muted rounded-md" : "")}
      >
        <Button asChild size="icon" variant="ghost" className="p-2">
          <SettingsIcon />
        </Button>
      </NavLink>
    </header>
  );
}

export default Header;
