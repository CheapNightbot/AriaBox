import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { downloadTrack } from "@/lib/api"
import { cn } from "@/lib/utils"
import type { Album, Track } from "@/types"
import { DownloadIcon, FileAudio } from "lucide-react"
import { useEffect, useState } from "react"
import { toast } from "sonner"

interface DownloadDialogProps {
    track: Track | null
    album: Album | null
    open: boolean
    onOpenChange: (open: boolean) => void
    promptForFormat: boolean
    defaultFormat: string
}

export default function DownloadDialog({
    track,
    album,
    open,
    onOpenChange,
    promptForFormat,
    defaultFormat,
}: DownloadDialogProps) {
    const [selectedFormat, setSelectedFormat] = useState(defaultFormat)
    const [isDownloading, setIsDownloading] = useState(false)
    const [loadingMessageIndex, setLoadingMessageIndex] = useState(0)

    const loadingMessages = [
        "Fetching audio stream...",
        "Converting to best quality...",
        "Applying beautiful metadata...",
        "Almost there...",
    ]

    // Reset format when dialog opens or default changes
    useEffect(() => {
        if (open) {
            setSelectedFormat(defaultFormat)
        }
    }, [open, defaultFormat])

    // Dynamic loading messages
    useEffect(() => {
        if (isDownloading) {
            const interval = setInterval(() => {
                setLoadingMessageIndex((prev) => (prev + 1) % loadingMessages.length)
            }, 10000) // change every 10 seconds ~
            return () => clearInterval(interval)
        } else {
            setLoadingMessageIndex(0)
        }
    }, [isDownloading])

    // If prompt is disabled, download immediately when opened!
    useEffect(() => {
        if (open && !promptForFormat && !isDownloading) {
            handleDownload(defaultFormat)
        }
    }, [open, promptForFormat, defaultFormat])

    const isTrack = !!track
    const displayTitle = isTrack ? track?.title : album?.title
    const displayArtists = isTrack
        ? track?.artists?.map((a) => a.name).join(", ")
        : album?.artists?.map((a) => a.name).join(", ")
    const displayAlbum = isTrack
        ? track?.album?.title
        : `${album?.total_tracks ?? "?"} tracks`

    const displayCover = isTrack
        ? track?.album?.cover
        : album?.cover

    const handleDownload = async (format: string) => {
        const itemToDownload = track || album
        if (!itemToDownload) return

        setIsDownloading(true)
        try {
            const normalizedService = itemToDownload.service_name?.toLowerCase() || ""
            const service =
                normalizedService.includes("itunes") || normalizedService.includes("apple")
                    ? "itunes"
                    : normalizedService.includes("youtube")
                        ? "ytmusic"
                        : "deezer"

            const response = await downloadTrack(
                isTrack ? itemToDownload.id : undefined,
                !isTrack ? itemToDownload.id : undefined,
                service,
                format,
            )

            const contentType = response.headers.get("content-type")

            if (contentType?.includes("application/json")) {
                const data = (await response.json()) as { message: string }
                toast.success(data.message)
            } else {
                const blob = await response.blob()
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement("a")
                a.href = url

                const disposition = response.headers.get("content-disposition")
                let filename = `downloaded.${format}`

                if (disposition) {
                    const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i)
                    if (utf8Match && utf8Match[1]) {
                        filename = decodeURIComponent(utf8Match[1].trim())
                    } else {
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

                toast.success("Downloaded successfully! 🎵")
            }

            onOpenChange(false)
        } catch (err) {
            const message = err instanceof Error ? err.message : "Failed to download"
            toast.error(message)
        } finally {
            setIsDownloading(false)
        }
    }

    if (!track && !album) return null

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="min-w-fit">
                <DialogHeader>
                    <DialogTitle>
                        {isTrack ? "Download Track" : "Download Album"}
                    </DialogTitle>
                    <DialogDescription>
                        {promptForFormat
                            ? "Select your preferred audio format below."
                            : "Preparing download..."}
                    </DialogDescription>
                </DialogHeader>

                {/* Metadata Summary Card */}
                <div className="flex items-center gap-4 p-4 bg-muted rounded-lg">
                    <Avatar className="w-16 h-16 border rounded">
                        <AvatarImage src={displayCover} className="rounded" />
                        <AvatarFallback className="text-xl rounded">🎵</AvatarFallback>
                    </Avatar>
                    <div className="flex flex-col overflow-hidden flex-1">
                        <span className="font-bold text-base truncate">{displayTitle}</span>
                        <span className="text-sm text-muted-foreground truncate">
                            {displayArtists ?? "Unknown Artist"}
                        </span>
                        <span className="text-xs text-muted-foreground truncate">
                            {displayAlbum}
                        </span>
                    </div>
                </div>

                {isDownloading ? (
                    <div className="flex flex-col items-center gap-4 w-full py-4 animate-in fade-in duration-300">
                        <FileAudio className="w-10 h-10 text-primary animate-pulse" />
                        <p
                            className="font-semibold text-sm animate-in fade-in duration-300"
                            key={loadingMessageIndex}
                        >
                            {loadingMessages[loadingMessageIndex]}
                        </p>
                        <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                            <div className="h-full w-1/2 animate-shimmer rounded-full bg-primary" />
                        </div>
                    </div>
                ) : (
                    <div className="space-y-4 py-2 animate-in fade-in duration-300">
                        {promptForFormat && (
                            <div className="grid grid-cols-3 gap-2">
                                {["mp3", "flac", "opus", "ogg", "m4a", "wav"].map((fmt) => (
                                    <button
                                        key={fmt}
                                        onClick={() => setSelectedFormat(fmt)}
                                        className={cn(
                                            "flex items-center justify-center rounded-lg border-2 p-3 text-sm font-semibold transition-all capitalize",
                                            selectedFormat === fmt
                                                ? "border-primary bg-primary/5 text-primary shadow-sm"
                                                : "border-muted bg-background text-muted-foreground hover:border-primary/50 hover:bg-muted/50",
                                        )}
                                    >
                                        {fmt}
                                    </button>
                                ))}
                            </div>
                        )}

                        <DialogFooter className="justify-center! gap-2">
                            <Button variant="outline" onClick={() => onOpenChange(false)}>
                                Cancel
                            </Button>
                            <Button
                                onClick={() => handleDownload(selectedFormat)}
                                className="gap-2"
                            >
                                <DownloadIcon className="w-4 h-4" />
                                Download
                            </Button>
                        </DialogFooter>
                    </div>
                )}
            </DialogContent>
        </Dialog>
    )
}
