import axios from "axios";

// Use relative URL in browser so requests flow through the Vercel rewrite proxy
// (/api/v1/* → NEXT_PUBLIC_API_URL/api/v1/*), avoiding CSP and CORS issues.
// Fall back to absolute URL for SSR contexts.
const API_BASE =
  typeof window !== "undefined"
    ? "/api/v1"
    : `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1`;

export const apiClient = axios.create({
  baseURL: API_BASE,
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
