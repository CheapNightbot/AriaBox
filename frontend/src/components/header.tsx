import DevTools from "@/components/dev-tools"
import { Button } from "@/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import "@/styles/header.css"
import { ArrowLeftIcon, FileMusicIcon, SettingsIcon } from "lucide-react"
import { NavLink, useLocation, useNavigate } from "react-router"

function Header() {
  const location = useLocation()
  const navigate = useNavigate()

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
        className="select-none text-3xl font-semibold tracking-wide hover:cursor-pointer animate-in fade-in blur-in-sm duration-500 ease-in-out w-fit mx-auto"
        onClick={() => (window.location.href = "/")}
      >
        AriaBox ⨾<span className="rotate">💿</span>✮˚.⋆
      </h1>

      <div className="absolute right-0 flex items-center gap-2">
        {import.meta.env.DEV && <DevTools />}

        <NavLink
          to="/convert"
          className={({ isActive }) => (isActive ? "bg-muted rounded-md" : "")}
        >
          <Tooltip delayDuration={500}>
            <TooltipTrigger>
              <Button asChild size="icon" variant="ghost" className="p-2">
                <FileMusicIcon />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Convert Audio</p>
            </TooltipContent>
          </Tooltip>
        </NavLink>

        <NavLink
          to="/settings"
          className={({ isActive }) => (isActive ? "bg-muted rounded-md" : "")}
        >
          <Tooltip delayDuration={500}>
            <TooltipTrigger>
              <Button asChild size="icon" variant="ghost" className="p-2">
                <SettingsIcon />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Settings</p>
            </TooltipContent>
          </Tooltip>
        </NavLink>
      </div>
    </header>
  )
}

export default Header
