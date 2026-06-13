import type { AppSettings } from "@/types";

const API_BASE_URL = "/api";

export async function fetchSettings(): Promise<AppSettings> {
  const response = await fetch(`${API_BASE_URL}/settings`);

  if (!response.ok) {
    throw new Error("Failed to fetch settings from backend...(´;ω;`)");
  }

  return response.json();
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

  return response.json();
}
