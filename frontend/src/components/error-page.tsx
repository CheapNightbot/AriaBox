import { ScrollArea } from "@/components/ui/scroll-area";
import { SearchAlertIcon } from "lucide-react";

function ErrorPage() {
  return (
    <ScrollArea className="border h-[clamp(600px,85vh,830px)] w-[clamp(600px,90vw,1200px)] rounded-sm pt-8">
      <div className="h-[clamp(600px,70vh,700px)] w-full  animate-in fade-in-60 zoom-in-80 duration-500 ease-in-out flex flex-col items-center py-10">
        <h2 className="scroll-m-20 pb-2 text-3xl font-semibold tracking-tight first:mt-0">
          404 NOT FOUND
        </h2>
        <p>We can't seem to find the page you're looking for.</p>
        <div className="flex flex-col flex-1 items-center justify-center gap-4">
          <SearchAlertIcon size={100} className="animate-pulse" />
        </div>
      </div>
    </ScrollArea>
  );
}

export default ErrorPage;
