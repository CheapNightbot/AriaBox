import Header from "@/components/header";
import SearchForm from "@/components/search-form";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import type { SearchResults } from "@/types";
import { useState } from "react";
import { Toaster } from "sonner";
import Footer from "@/components/footer";
import { MusicTable } from "@/components/music-table";
import { cn } from "./lib/utils";

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResults>({
    albums: [],
    artists: [],
    tracks: [],
  });

  const gotResults = (obj) => {
    if (!obj || typeof obj !== "object" || Object.keys(obj).length === 0) {
      return false;
    }

    return Object.values(obj).some(
      (value) => Array.isArray(value) && value.length > 0,
    );
  };

  return (
    <>
      <Toaster richColors />
      <Header />
      <SearchForm
        loading={loading}
        setLoading={setLoading}
        setResults={setResults}
      />
      <ScrollArea
        className={cn(
          "border h-[clamp(600px,70vh,800px)] w-[clamp(600px,90vw,1200px)] rounded-sm",
          gotResults(results) && "rounded-tl-none",
        )}
      >
        {loading ? (
          <div className="h-[clamp(600px,70vh,700px)] w-full grid place-items-center">
            <p className="text-xl text-muted-foreground animate-in fade-in-60 zoom-in-80 duration-500 ease-in-out">
              <span className="animate-pulse">Searching...𓏲 ๋࣭ ࣪ ˖🎐</span>
            </p>
          </div>
        ) : gotResults(results) ? (
          <MusicTable musicList={results} />
        ) : (
          <div className="h-[clamp(600px,70vh,700px)] w-full grid place-items-center">
            <p className="text-xl text-muted-foreground animate-in fade-in-60 zoom-in-80 duration-500 ease-in-out">
              Nothing to show here...⋆｡‧˚ʚ🧸ɞ˚‧｡⋆
            </p>
          </div>
        )}
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
      <Footer />
    </>
  );
}

export default App;
