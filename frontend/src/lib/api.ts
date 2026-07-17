import type { AppSettings, SearchResults, UploadResponse } from "@/types";
import { toast } from "sonner";

const API_BASE_URL = "/api";

export async function fetchSettings(): Promise<AppSettings> {
  const response = await fetch(`${API_BASE_URL}/settings`);

  if (!response.ok) {
    throw new Error("Failed to fetch settings from backend...(´;ω;`)");
  }

  return response.json() as Promise<AppSettings>;
}

export async function updateSettings(
  newSettings: Partial<AppSettings>,
): Promise<AppSettings> {
  const response = await fetch(`${API_BASE_URL}/settings`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(newSettings),
  });

  if (!response.ok) {
    throw new Error("Something went wrong updating settings...(,,>﹏<,,)");
  }

  return response.json() as Promise<AppSettings>;
}

export async function searchMusic(payload: {
  artist?: string;
  song?: string;
  music_url?: string;
  search_method: "named_search" | "url_search";
}): Promise<SearchResults> {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorMessage = `Server error: ${response.status}`;
    try {
      const errorData = (await response.json()) as { message: string };
      if (errorData.message) {
        errorMessage = errorData.message;
      }
    } catch {
      // Ignore if the error response isn't valid JSON
    }
    throw new Error(errorMessage);
  }

  const data = (await response.json()) as { results: Promise<SearchResults> };
  return data.results;
}

export async function uploadAudioFile(
  file: File,
  onProgress?: (progress: number) => void,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return new Promise<UploadResponse>((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.open("POST", `${API_BASE_URL}/upload`);

    // Track upload progress
    if (onProgress) {
      xhr.upload.onprogress = (event: ProgressEvent) => {
        if (event.lengthComputable) {
          const percentCompleted = Math.round(
            (event.loaded * 100) / event.total,
          );
          onProgress(percentCompleted);
        }
      };
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const data = JSON.parse(xhr.responseText) as UploadResponse;
          resolve(data);
        } catch (parseError) {
          reject(
            new Error("Failed to parse server response", { cause: parseError }),
          );
        }
      } else {
        let errorMessage = "Upload failed!";
        try {
          const errorData = JSON.parse(xhr.responseText) as {
            message?: string;
          };
          errorMessage = errorData?.message ?? errorMessage;
        } catch {
          // Fall back to default message
        }
        reject(new Error(errorMessage, { cause: xhr.status }));
      }
    };

    xhr.onerror = () => {
      reject(
        new Error("Network error occurred during upload!", {
          cause: xhr.statusText,
        }),
      );
    };

    xhr.send(formData);
  });
}

export async function deleteAudioFile(file_id: string, file_ext: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/delete`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_id, file_ext }),
    });

    if (!response.ok) {
      const errorData = (await response.json().catch(() => null)) as {
        message: string;
      };
      const errorMessage =
        errorData?.message || `Delete failed: ${response.status}`;
      toast.error(errorMessage);
    }
  } catch {
    toast.error("Failed to delete file. Network error.");
  }
}

export async function applyMetadata(
  fileId: string,
  fileExt: string,
  trackId?: number,
  albumId?: number,
  service?: string,
  overwrite = true,
): Promise<Response> {
  const response = await fetch(`${API_BASE_URL}/tag`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      file_id: fileId,
      file_ext: fileExt,
      track_id: trackId,
      album_id: albumId,
      service: service,
      overwrite: overwrite,
    }),
  });

  if (!response.ok) {
    let errorMessage = `Server error: ${response.status}`;
    try {
      const errorData = (await response.json()) as { message?: string };
      if (errorData.message) {
        errorMessage = errorData.message;
      }
    } catch {
      // Ignore if not valid JSON
    }
    throw new Error(errorMessage);
  }

  return response;
}
