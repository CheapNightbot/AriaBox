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
import { formatDuration } from "@/lib/utils";
import type { SearchResults } from "@/types";
import { MoreHorizontalIcon, UserIcon } from "lucide-react";

export function MusicTable({ musicList }: { musicList: SearchResults }) {
  return (
    <Tabs defaultValue="tracks">
      <TabsList className="absolute -translate-y-[2.6rem] -translate-x-[0.1rem] rounded-t">
        <TabsTrigger value="tracks">Tracks</TabsTrigger>
        <TabsTrigger value="albums">Albums</TabsTrigger>
        <TabsTrigger value="artists">Artists</TabsTrigger>
      </TabsList>
      <TabsContent value="tracks">
        {musicList.tracks.length === 0 ? (
          <div className="h-[clamp(600px,70vh,700px)] w-full grid place-items-center">
            <p className="text-xl text-muted-foreground animate-in fade-in-60 zoom-in-80 duration-500 ease-in-out">
              Nothing to show here...⋆｡‧˚ʚ🧸ɞ˚‧｡⋆
            </p>
          </div>
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
                <TableHead className="text-center font-semibold">🎀</TableHead>
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
                          <HoverCard
                            key={artist.id}
                            openDelay={100}
                            closeDelay={100}
                          >
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
                            {idx !== (track.artists?.length ?? 0) - 1 && (
                              <>,&nbsp;</>
                            )}
                          </HoverCard>
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
                          <DropdownMenuItem>Save</DropdownMenuItem>
                          <DropdownMenuItem>Download</DropdownMenuItem>
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

      <TabsContent value="albums">
        {musicList.albums.length === 0 ? (
          <div className="h-[clamp(600px,70vh,700px)] w-full grid place-items-center">
            <p className="text-xl text-muted-foreground animate-in fade-in-60 zoom-in-80 duration-500 ease-in-out">
              Nothing to show here...⋆｡‧˚ʚ🧸ɞ˚‧｡⋆
            </p>
          </div>
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
                <TableHead className="text-center font-semibold">🎀</TableHead>
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
                          <HoverCard
                            key={artist.id}
                            openDelay={100}
                            closeDelay={100}
                          >
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
                            {idx !== (album.artists?.length ?? 0) - 1 && (
                              <>,&nbsp;</>
                            )}
                          </HoverCard>
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
                          <DropdownMenuItem>Save</DropdownMenuItem>
                          <DropdownMenuItem>Download</DropdownMenuItem>
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

      <TabsContent value="artists">
        {musicList.artists.length === 0 ? (
          <div className="h-[clamp(600px,70vh,700px)] w-full grid place-items-center">
            <p className="text-xl text-muted-foreground animate-in fade-in-60 zoom-in-80 duration-500 ease-in-out">
              Nothing to show here...⋆｡‧˚ʚ🧸ɞ˚‧｡⋆
            </p>
          </div>
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
              </TableRow>
            </TableHeader>
            <TableBody>
              {musicList.artists.map((artist) => {
                return (
                  <TableRow key={artist.id} className="text-center">
                    <TableCell className="w-25 pl-4">
                      <Avatar className="size-20">
                        <AvatarImage className="rounded" src={artist.picture} />
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
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </TabsContent>
    </Tabs>
  );
}
