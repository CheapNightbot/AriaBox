export interface Artist {
  artists?: Artist[]; // Handled in Album, but strictly speaking Artist doesn't have artists, this is just for reference if needed
  genres?: string[];
  id?: number;
  name?: string;
  picture?: string;
  role?: string;
  url?: string;

  // Metadata about the music platform/service
  service_name?: string;
  service_url?: string;
}

export interface Album {
  artists?: Artist[];
  cover?: string;
  duration?: number;
  explicit?: boolean;
  genres?: string[];
  id?: number;
  label?: string;
  release_date?: string;
  title?: string;
  total_tracks?: number;
  tracks?: Track[];
  type?: string;
  upc?: string;
  url?: string;

  // Metadata about the music platform/service
  service_name?: string;
  service_url?: string;
}

export interface Track {
  album?: Album;
  artists?: Artist[];
  bpm?: number;
  duration?: number;
  explicit?: boolean;
  genre?: string;
  gain?: number;
  id?: number;
  isrc?: string;
  preview_url?: string;
  release_date?: string;
  title?: string;
  track_number?: number;
  url?: string;

  // Metadata about the music platform/service
  service_name?: string;
  service_url?: string;
}

export interface SearchResults {
  albums: Album[];
  artists: Artist[];
  tracks: Track[];
}

export interface AppSettings {
  language: string;
  location: string;
  enable_downloads: boolean;
  auto_save_to_library: boolean;
  download_format: "mp3" | "flac" | "opus" | "ogg" | "m4a" | "wav";
  prompt_for_format: boolean;
}

export interface UploadResponse {
  file_id: string;
  original_filename: string;
  suggested_artist: string;
  suggested_song: string;
}
