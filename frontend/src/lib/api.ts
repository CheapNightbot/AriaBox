import type { AppSettings, SearchResults } from "@/types";

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
