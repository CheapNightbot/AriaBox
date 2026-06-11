import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatDuration } from "@/lib/utils";
import type { SearchResults } from "@/types";
import { MoreHorizontalIcon } from "lucide-react";

export function MusicTable({ musicList }: { musicList: SearchResults }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="text-center font-semibold"></TableHead>
          <TableHead className="text-center font-semibold">Title</TableHead>
          <TableHead className="text-center font-semibold">Artists</TableHead>
          <TableHead className="text-center font-semibold">Album</TableHead>
          <TableHead className="text-center font-semibold">Duration</TableHead>
          <TableHead className="text-center font-semibold">🎀</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {musicList.tracks.map((track) => {
          return (
            <TableRow key={track.id} className="text-center">
              <TableCell className="w-25 pl-4">
                <Avatar className="size-20">
                  <AvatarImage className="rounded" src={track.album.cover} />
                  <AvatarFallback className="rounded">
                    <Skeleton />
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
                {track.artists.map((artist, idx) => {
                  return (
                    <>
                      <a
                        key={artist.id}
                        href={artist.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:underline"
                      >
                        {artist.name}
                      </a>
                      {idx !== track.artists.length - 1 && <>, </>}
                    </>
                  );
                })}
              </TableCell>
              <TableCell className="whitespace-normal wrap-break-word">
                {track.album.url ? (
                  <a
                    href={track.album.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:underline"
                  >
                    {track.album.title}
                  </a>
                ) : (
                  track.album.title || track.title
                )}
              </TableCell>
              <TableCell>{formatDuration(track.duration)}</TableCell>
              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="size-8">
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
  );
}
