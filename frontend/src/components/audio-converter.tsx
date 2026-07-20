import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { convertAudio } from "@/lib/api"
import { cn } from "@/lib/utils"
import { DownloadIcon, FileAudioIcon, Loader2Icon, UploadIcon, XIcon } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

const SUPPORTED_FORMATS = ["mp3", "flac", "opus", "ogg", "m4a", "wav"]

export default function AudioConverter() {
  const [file, setFile] = useState<File | null>(null)
  const [targetFormat, setTargetFormat] = useState("flac")
  const [isDragging, setIsDragging] = useState(false)
  const [isConverting, setIsConverting] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleConvert = async () => {
    if (!file) return

    setIsConverting(true)
    try {
      const response = await convertAudio(file, targetFormat)

      // File download (binary response)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url

      // Get filename from Content-Disposition header
      const disposition = response.headers.get("content-disposition")
      let filename = `converted.${targetFormat}` // Safe fallback with extension

      if (disposition) {
        // Try to match UTF-8 encoded filenames first (e.g., filename*=UTF-8''%E3%83%A8...)
        const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i)
        if (utf8Match && utf8Match[1]) {
          filename = decodeURIComponent(utf8Match[1].trim())
        } else {
          // Fallback to regular filename="..." (NO 'g' FLAG!)
          const regularMatch = disposition.match(/filename="?([^";]+)"?/i)
          if (regularMatch && regularMatch[1]) {
            filename = regularMatch[1].trim()
          }
        }
      }

      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)

      toast.success("Audio converted and downloaded successfully! 🎵")
      setFile(null)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to convert audio")
    } finally {
      setIsConverting(false)
    }
  }

  return (
    <section>
      <header className="w-[clamp(400px,90vw,1200px)] py-3 h-30 animate-in fade-in slide-in-from-top-10 duration-500 ease-in-out">
        <h2 className="scroll-m-20 pb-2 text-2xl font-semibold tracking-tight">
          Convert Audio
        </h2>
        <p className="text-muted-foreground">
          Easily convert your audio files between formats like MP3, FLAC, and Opus.
          Your original metadata and cover art are automatically preserved and optimized!
        </p>
      </header>

      <ScrollArea className="h-[clamp(600px,70vh,800px)] w-[clamp(600px,90vw,1200px)] rounded-sm">
        <div className="flex flex-col gap-6 items-center animate-in zoom-in-95 fade-in ease-in-out duration-500 p-8 h-[clamp(600px,70vh,665px)]">

          {/* Upload Area */}
          {!file ? (
            <div
              className={cn(
                "h-full border-2 border-dashed rounded-xl flex flex-col items-center justify-center gap-4 transition-colors cursor-pointer w-[clamp(600px,80vw,800px)] animate-in blur-in zoom-in-95 duration-500 ease-in-out",
                isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50 hover:bg-primary/5"
              )}
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => document.getElementById("file-upload")?.click()}
            >
              <UploadIcon className="w-12 h-12 text-muted-foreground" />
              <div className="text-center">
                <p className="font-medium">Drag & drop your audio file here</p>
                <p className="text-sm text-muted-foreground">or click to browse</p>
              </div>
              <input
                id="file-upload"
                type="file"
                accept="audio/*"
                className="hidden"
                onChange={handleFileChange}
              />
            </div>
          ) : (
            <div
              key={`file-card-${file.name}`}
              className="w-full p-4 border rounded-xl bg-muted/30 flex items-center justify-between gap-4 animate-in fade-in slide-in-from-top-4 duration-300"
            >
              <div className="flex items-center gap-3 overflow-hidden">
                <FileAudioIcon className="w-8 h-8 text-primary flex-shrink-0" />
                <div className="min-w-0">
                  <p className="font-medium truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setFile(null)}
                disabled={isConverting}
              >
                <XIcon className="w-4 h-4" />
              </Button>
            </div>
          )}

          {/* Format Selection Chips */}
          {file && (
            <div
              key={`format-chips-${file.name}`}
              className="w-full space-y-3 animate-in fade-in slide-in-from-bottom-4 duration-500"
            >
              <p className="text-sm font-medium text-center">Select Target Format</p>
              <div className="flex flex-wrap justify-center gap-2">
                {SUPPORTED_FORMATS.map((fmt) => (
                  <button
                    key={fmt}
                    onClick={() => setTargetFormat(fmt)}
                    className={cn(
                      "px-4 py-2 rounded-full text-sm font-semibold transition-all border animate-in zoom-in-95 fade-in duration-500 ease-in-out",
                      targetFormat === fmt
                        ? "bg-primary text-primary-foreground border-primary shadow-sm"
                        : "bg-background text-muted-foreground border-muted hover:border-primary/50"
                    )}
                  >
                    {fmt.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Convert Button */}
          {file && (
            <div
              key={`convert-btn-${file.name}`}
              className="animate-in zoom-in-90 fade-in slide-in-from-bottom-4 duration-700"
            >
              <Button
                size="lg"
                className="w-full max-w-xs gap-2"
                onClick={handleConvert}
                disabled={isConverting}
              >
                {isConverting ? (
                  <>
                    <Loader2Icon className="w-4 h-4 animate-spin" />
                    Converting...
                  </>
                ) : (
                  <>
                    <DownloadIcon className="w-4 h-4" />
                    Convert & Download
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
      </ScrollArea>
    </section>
  )
}
