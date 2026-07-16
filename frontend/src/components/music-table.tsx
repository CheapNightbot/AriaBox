import { AppleMusicIcon, DeezerIcon, YouTubeMusicIcon } from "@/assets/icons";
import ApplyMetadataDialog from "@/components/apply-metadata-dialog";
import EmptyState from "@/components/empty-state";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { fetchSettings } from "@/lib/api";
import { formatDuration } from "@/lib/utils";
import type { Album, Artist, SearchResults, Track } from "@/types";
import { MoreHorizontalIcon, UserIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { toast } from "sonner";

export function MusicTable({ musicList }: { musicList: SearchResults }) {
  const navigate = useNavigate();
  const [enableDownloads, setEnableDownloads] = useState<boolean>(false);

  const [selectedTrack, setSelectedTrack] = useState<Track | null>(null);
  const [selectedAlbum, setSelectedAlbum] = useState<Album | null>(null);

  useEffect(() => {
    async function loadSettings() {
      try {
        const data = await fetchSettings();
        setEnableDownloads(data.enable_downloads);
      } catch (error) {
        const msg = error instanceof Error ? error.message : "Unknown error";
        toast.error(`Failed to fetch download settings: ${msg}`);
      }
    }
    void loadSettings();
  }, []);

  const handleDownload = (
    event: React.MouseEvent<HTMLDivElement, MouseEvent>,
  ) => {
    if (!enableDownloads) {
      event.preventDefault();
      toast.info(
        <p>
          The downloading feature is disabled by default! If possible, please
          support artists and purchase the music you love! You can enable this
          feature in{" "}
          <span
            className="underline hover:cursor-pointer hover:text-accent"
            onClick={() => void navigate("/settings")}
          >
            Settings
          </span>
          .
        </p>,
      );
    } else {
      toast.warning("Download: NOT IMPLEMENTED YET!");
    }
  };

  return (
    <>
      <Tabs defaultValue="tracks">
        <TabsList className="absolute translate-y-[-2.6rem] translate-x-[-0.1rem] rounded-t">
          <TabsTrigger value="tracks">Tracks</TabsTrigger>
          <TabsTrigger value="albums">Albums</TabsTrigger>
          <TabsTrigger value="artists">Artists</TabsTrigger>
        </TabsList>

        {/* --- TRACKS TAB --- */}
        <TabsContent value="tracks">
          {musicList.tracks.length === 0 ? (
            <EmptyState />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-center font-semibold"></TableHead>
                  <TableHead className="text-center font-semibold">
                    Title
                  </TableHead>
                  <TableHead className="text-center font-semibold">
                    Artists
                  </TableHead>
                  <TableHead className="text-center font-semibold">
                    Album
                  </TableHead>
                  <TableHead className="text-center font-semibold">
                    Duration
                  </TableHead>
                  <TableHead className="text-center font-semibold">
                    🎀
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {musicList.tracks.map((track) => {
                  return (
                    <TableRow key={track.id} className="text-center">
                      <TableCell className="w-25 pl-4">
                        <Avatar className="size-20">
                          <AvatarImage
                            className="rounded"
                            src={track.album?.cover}
                          />
                          <AvatarFallback className="rounded overflow-clip">
                            <Skeleton className="size-full" />
                          </AvatarFallback>
                        </Avatar>
                      </TableCell>
                      <TableCell className="whitespace-normal wrap-break-word">
                        <a
                          href={track.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:underline"
                        >
                          {track.title}
                        </a>
                      </TableCell>
                      <TableCell className="whitespace-normal wrap-break-word">
                        {track.artists?.map((artist, idx) => {
                          return (
                            <div key={artist.id} className="contents">
                              <ArtistHoverCard artist={artist} />
                              {idx !== (track.artists?.length ?? 0) - 1 && (
                                <>,&nbsp;</>
                              )}
                            </div>
                          );
                        })}
                      </TableCell>
                      <TableCell className="whitespace-normal wrap-break-word">
                        {track.album?.url ? (
                          <a
                            href={track.album?.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:underline"
                          >
                            {track.album?.title}
                          </a>
                        ) : (
                          (track.album?.title ?? track.title)
                        )}
                      </TableCell>
                      <TableCell>{formatDuration(track.duration)}</TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="size-8"
                            >
                              <MoreHorizontalIcon />
                              <span className="sr-only">Open menu</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem
                              onClick={() => {
                                setSelectedTrack(track);
                                setSelectedAlbum(null);
                              }}
                            >
                              Apply Metadata
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              disabled={!enableDownloads}
                              onClick={(e) => handleDownload(e)}
                            >
                              Download
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </TabsContent>

        {/* --- ALBUMS TAB --- */}
        <TabsContent value="albums">
          {musicList.albums.length === 0 ? (
            <EmptyState />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-center font-semibold"></TableHead>
                  <TableHead className="text-center font-semibold">
                    Title
                  </TableHead>
                  <TableHead className="text-center font-semibold">
                    Artists
                  </TableHead>
                  <TableHead className="text-center font-semibold">
                    Tracks
                  </TableHead>
                  <TableHead className="text-center font-semibold">
                    🎀
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {musicList.albums.map((album) => {
                  return (
                    <TableRow key={album.id} className="text-center">
                      <TableCell className="w-25 pl-4">
                        <Avatar className="size-20">
                          <AvatarImage className="rounded" src={album.cover} />
                          <AvatarFallback className="rounded overflow-clip">
                            <Skeleton className="size-full" />
                          </AvatarFallback>
                        </Avatar>
                      </TableCell>
                      <TableCell className="whitespace-normal wrap-break-word">
                        <a
                          href={album.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:underline"
                        >
                          {album.title}
                        </a>
                      </TableCell>
                      <TableCell className="whitespace-normal wrap-break-word">
                        {album.artists?.map((artist, idx) => {
                          return (
                            <>
                              <ArtistHoverCard artist={artist} />
                              {idx !== (album.artists?.length ?? 0) - 1 && (
                                <>,&nbsp;</>
                              )}
                            </>
                          );
                        })}
                      </TableCell>
                      <TableCell className="whitespace-normal wrap-break-word">
                        {album.total_tracks}
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="size-8"
                            >
                              <MoreHorizontalIcon />
                              <span className="sr-only">Open menu</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem
                              onClick={() => {
                                setSelectedAlbum(album);
                                setSelectedTrack(null);
                              }}
                            >
                              Apply Metadata
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              disabled={!enableDownloads}
                              onClick={(e) => handleDownload(e)}
                            >
                              Download
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </TabsContent>

        {/* --- ARTISTS TAB --- */}
        <TabsContent value="artists">
          {musicList.artists.length === 0 ? (
            <EmptyState />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-center font-semibold"></TableHead>
                  <TableHead className="text-center font-semibold">
                    Name
                  </TableHead>
                  <TableHead className="text-center font-semibold">
                    Genres
                  </TableHead>
                  <TableHead className="text-center font-semibold">
                    🎀
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {musicList.artists.map((artist) => {
                  return (
                    <TableRow key={artist.id} className="text-center">
                      <TableCell className="w-25 pl-4">
                        <Avatar className="size-20">
                          <AvatarImage
                            className="rounded"
                            src={artist.picture}
                          />
                          <AvatarFallback className="rounded overflow-clip">
                            <UserIcon />
                          </AvatarFallback>
                        </Avatar>
                      </TableCell>
                      <TableCell className="whitespace-normal wrap-break-word">
                        <a
                          href={artist.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:underline"
                        >
                          {artist.name}
                        </a>
                      </TableCell>
                      <TableCell className="whitespace-normal wrap-break-word">
                        {artist.genres?.length === 0
                          ? "Unknown"
                          : artist.genres?.map((genre, idx) => {
                              return (
                                <p key={idx}>
                                  {genre}
                                  {idx !== (artist.genres?.length ?? 0) - 1 && (
                                    <>, </>
                                  )}
                                </p>
                              );
                            })}
                      </TableCell>
                      <TableCell align="center">
                        {artist.service_name === "Deezer" ? (
                          <DeezerIcon className="text-deezer" />
                        ) : artist.service_name === "iTunes" ? (
                          <AppleMusicIcon className="text-apple-music" />
                        ) : (
                          <YouTubeMusicIcon className="text-yt-music" />
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </TabsContent>
      </Tabs>
      <ApplyMetadataDialog
        track={selectedTrack}
        album={selectedAlbum}
        open={!!selectedTrack || !!selectedAlbum}
        onOpenChange={(isOpen) => {
          if (!isOpen) {
            setSelectedTrack(null);
            setSelectedAlbum(null);
          }
        }}
      />
    </>
  );
}

function ArtistHoverCard({ artist }: { artist: Artist }) {
  return (
    <HoverCard key={artist.id} openDelay={100} closeDelay={100}>
      <HoverCardTrigger asChild>
        <a
          href={artist.url}
          target="_blank"
          rel="noopener noreferrer"
          className="hover:underline"
        >
          {artist.name}
        </a>
      </HoverCardTrigger>
      <HoverCardContent className="rounded flex items-center gap-4">
        <Avatar className="size-12">
          <AvatarImage src={artist.picture} />
          <AvatarFallback className="overflow-clip">
            <Skeleton className="size-full" />
          </AvatarFallback>
        </Avatar>
        <p className="text-lg">{artist.name}</p>
      </HoverCardContent>
    </HoverCard>
  );
}
