import Footer from "@/components/footer"
import Header from "@/components/header"
import { TooltipProvider } from "@/components/ui/tooltip"
import { Outlet } from "react-router"
import { Toaster } from "sonner"

function BaseLayout() {
  return (
    <>
      <TooltipProvider>
        <Toaster richColors />
        <Header />
        <Outlet />
        <Footer />
      </TooltipProvider>
    </>
  )
}

export default BaseLayout
