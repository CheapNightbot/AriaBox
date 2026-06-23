import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { deleteAudioFile, uploadAudioFile } from "@/lib/api";
import type { Album, Track } from "@/types";
import { AlertCircle, CheckCircle2, FileAudio, Upload } from "lucide-react";
import {
  type ChangeEvent,
  type DragEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import { toast } from "sonner";

interface ApplyMetadataDialogProps {
  track: Track | null;
  album: Album | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

function ApplyMetadataDialog({
  track,
  album,
  open,
  onOpenChange,
}: ApplyMetadataDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<
    "idle" | "uploading" | "success" | "error"
  >("idle");
  const [fileId, setFileId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Reset everything when the dialog closes or the selection changes
  useEffect(() => {
    if (!open) {
      setFile(null);
      setProgress(0);
      setStatus("idle");
      setFileId(null);
      setErrorMsg(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }, [open, track, album]);

  const handleFileChange = async (selectedFile: File) => {
    setFile(selectedFile);
    setStatus("uploading");
    setProgress(0);
    setErrorMsg(null);

    try {
      const response = await uploadAudioFile(selectedFile, setProgress);
      setFileId(response.file_id);
      setStatus("success");
      toast.success("File uploaded successfully! ( ⸝⸝´꒳`⸝⸝)");
    } catch (err) {
      setStatus("error");
      setErrorMsg(err instanceof Error ? err.message : "Upload failed");
      toast.error("Upload failed. Please try again. (ó﹏ò｡)");
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) void handleFileChange(droppedFile);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) void handleFileChange(selected);
  };

  const handleReset = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFile(null);
    setFileId(null);
    setStatus("idle");
    setProgress(0);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleApply = () => {
    if (!fileId) return;

    // TODO: Will handle both track and album tagging here ~ !!!!
    if (track) {
      toast.info("Applying track metadata... (Coming soon!)");
    } else if (album) {
      toast.info("Applying album metadata... (Coming soon!)");
    }
  };

  // If neither track nor album is selected, don't render
  if (!track && !album) return null;

  // Determine what we're showing and get the display data
  const isTrack = !!track;
  const displayTitle = isTrack ? track?.title : album?.title;
  const displayArtists = isTrack
    ? track?.artists?.map((a) => a.name).join(", ")
    : album?.artists?.map((a) => a.name).join(", ");
  const displayAlbum = isTrack
    ? track?.album?.title
    : `${album?.total_tracks ?? "?"} tracks`;
  const displayCover = isTrack ? track?.album?.cover : album?.cover;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="min-w-fit">
        <DialogHeader>
          <DialogTitle>
            {isTrack ? "Apply Track Metadata" : "Apply Album Metadata"}
          </DialogTitle>
          <DialogDescription>
            Upload the audio file you want to tag with the selected{" "}
            {isTrack ? "track" : "album"}'s information.
          </DialogDescription>
        </DialogHeader>

        {/* The Metadata Summary Card */}
        <div className="flex items-center gap-4 p-4 bg-muted rounded-lg">
          <Avatar className="w-16 h-16 border rounded">
            <AvatarImage src={displayCover} className="rounded" />
            <AvatarFallback className="text-2xl rounded">🎵</AvatarFallback>
          </Avatar>
          <div className="flex flex-col overflow-hidden flex-1">
            <span className="font-bold text-lg truncate">{displayTitle}</span>
            <span className="text-sm text-muted-foreground truncate">
              {displayArtists ?? "Unknown Artist"}
            </span>
            <span className="text-xs text-muted-foreground truncate">
              {displayAlbum}
            </span>
          </div>
        </div>

        {/* The Dropzone Area */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() =>
            status !== "uploading" && fileInputRef.current?.click()
          }
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
            ${status === "success" ? "border-green-500 bg-green-50/50" : "border-gray-300 hover:border-primary hover:bg-muted/50"}
            ${status === "uploading" ? "cursor-wait" : ""}
          `}
        >
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept="audio/*"
            onChange={handleInputChange}
          />

          {status === "idle" && (
            <div className="flex flex-col items-center gap-2">
              <Upload className="w-10 h-10 text-muted-foreground" />
              <p className="font-semibold">Drag & Drop your audio file here</p>
              <p className="text-sm text-muted-foreground">
                or click to browse
              </p>
            </div>
          )}

          {status === "uploading" && (
            <div className="flex flex-col items-center gap-4 w-full">
              <FileAudio className="w-10 h-10 text-primary animate-pulse" />
              <p className="font-semibold">Uploading... {progress}%</p>
              <Progress value={progress} className="w-full h-2" />
            </div>
          )}

          {status === "success" && file && (
            <div className="flex flex-col items-center gap-2">
              <CheckCircle2 className="w-10 h-10 text-green-500" />
              <p className="font-semibold text-green-700">Ready to tag!</p>
              <p className="text-sm text-muted-foreground truncate max-w-full">
                {file.name}
              </p>
              <Button
                variant="link"
                className="text-xs h-auto p-0"
                disabled={isDeleting}
                onClick={(e) => {
                  e.stopPropagation();
                  setIsDeleting(true);
                  handleReset(e);
                  void deleteAudioFile(
                    fileId,
                    file.name.split(".").pop()?.toLowerCase() ?? "",
                  );
                  setIsDeleting(false);
                }}
              >
                {isDeleting ? "Removing..." : "Remove file"}
              </Button>
            </div>
          )}

          {status === "error" && (
            <div className="flex flex-col items-center gap-2 text-red-500">
              <AlertCircle className="w-10 h-10" />
              <p className="font-semibold">Upload Failed</p>
              <p className="text-sm">{errorMsg}</p>
              <Button
                variant="link"
                className="text-xs h-auto p-0 text-red-500"
                onClick={handleReset}
              >
                Try again
              </Button>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <DialogFooter className="justify-center! gap-2">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleApply} disabled={status !== "success"}>
            Apply Metadata & Download
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default ApplyMetadataDialog;
