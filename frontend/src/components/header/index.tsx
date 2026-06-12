import { Button } from "@/components/ui/button";
import { SettingsIcon } from "lucide-react";
import "./header.css";

function Header() {
  return (
    <header className="text-center flex items-center justify-center w-[clamp(400px,90vw,1200px)] py-4 mb-2">
      <h1
        id="header-logo"
        className="flex-1 select-none text-3xl font-semibold tracking-wide hover:cursor-pointer"
        onClick={() => (window.location.href = "/")}
      >
        AriaBox ⨾<span className="rotate">💿</span>✮˚.⋆
      </h1>

      <div className="">
        <Button size="icon" variant="ghost">
          <SettingsIcon className="size-1/2" />
        </Button>
      </div>
    </header>
  );
}

export default Header;
