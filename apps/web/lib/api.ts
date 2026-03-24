import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

// Attach Clerk token to every request
apiClient.interceptors.request.use(async (config) => {
  if (typeof window !== "undefined") {
    // Clerk exposes getToken on the window via ClerkProvider
    const { Clerk } = window as Window & { Clerk?: { session?: { getToken: () => Promise<string | null> } } };
    const token = await Clerk?.session?.getToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
