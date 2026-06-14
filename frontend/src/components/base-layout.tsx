import Footer from "@/components/footer";
import Header from "@/components/header";
import { Outlet } from "react-router";
import { Toaster } from "sonner";

function BaseLayout() {
  return (
    <>
      <Toaster richColors />
      <Header />
      <Outlet />
      <Footer />
    </>
  );
}

export default BaseLayout;
