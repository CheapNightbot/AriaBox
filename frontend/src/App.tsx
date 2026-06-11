import Header from "@/components/header";
import SearchForm from "@/components/search-form";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import type { SearchResults } from "@/types";
import { useState } from "react";
import { Toaster } from "sonner";
import Footer from "@/components/footer";
import { MusicTable } from "@/components/music-table";

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
      <ScrollArea className="border h-[clamp(600px,70vh,800px)] w-[clamp(600px,90vw,1200px)] rounded-sm">
        {loading ? (
          <div className="h-[clamp(600px,70vh,700px)] w-full grid place-items-center">
            <p className="text-xl text-muted-foreground animate-pulse">
              Searching...𓏲 ๋࣭ ࣪ ˖🎐
            </p>
          </div>
        ) : gotResults(results) ? (
          <MusicTable musicList={results} />
        ) : (
          <div className="h-[clamp(600px,70vh,700px)] w-full grid place-items-center">
            <p className="text-xl text-muted-foreground">
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
