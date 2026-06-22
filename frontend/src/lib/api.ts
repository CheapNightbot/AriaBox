import type { AppSettings, SearchResults, UploadResponse } from "@/types";
import axios, { type AxiosProgressEvent } from "axios";
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

  try {
    const response = await axios.post<UploadResponse>(
      `${API_BASE_URL}/upload`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent: AxiosProgressEvent) => {
          if (onProgress && progressEvent.total) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total,
            );
            onProgress(percentCompleted);
          }
        },
      },
    );

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      const errorData = error.response.data as { message?: string } | undefined;
      throw new Error(errorData?.message ?? "Upload failed!", { cause: error });
    }

    throw new Error("Network error occurred during upload!", { cause: error });
  }
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
