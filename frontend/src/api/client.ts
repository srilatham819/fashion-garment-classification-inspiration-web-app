export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

export type UploadResponse = {
  image_id: number;
  status: string;
};

export type SearchRequest = {
  query?: string;
  garment_type?: string;
  style?: string;
  material?: string;
  color?: string;
  pattern?: string;
  season?: string;
  occasion?: string;
  consumer_profile?: string;
  location_context?: string;
  limit: number;
};

export type SearchResult = {
  image_id: number;
  score: number | null;
  description: string | null;
  garment_type: string | null;
  style: string | null;
  material: string | null;
  color_palette: string[] | null;
  pattern: string | null;
  season: string | null;
  occasion: string | null;
  consumer_profile: string | null;
  location_context: string | null;
};

export type Annotation = {
  id: number;
  image_id?: number;
  note: string | null;
  tags: string | null;
  created_by: string | null;
};

export type Classification = {
  garment_type: string;
  style: string;
  material: string;
  color_palette: string[];
  pattern: string;
  season: string;
  occasion: string;
  consumer_profile: string;
  trend_notes: string;
  location_context: string;
  description: string;
};

export type LibraryImage = {
  id: number;
  original_filename: string;
  status: string;
  image_url: string;
  error_message: string | null;
  ai_metadata: Classification | null;
  annotations: Annotation[];
};

export function apiUrl(path: string): string {
  if (path.startsWith("http")) return path;
  return `${API_BASE_URL.replace(/\/api$/, "")}${path}`;
}

export async function checkHealth(): Promise<boolean> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.ok;
}

export async function listImages(): Promise<LibraryImage[]> {
  const response = await fetch(`${API_BASE_URL}/images`);
  if (!response.ok) {
    throw new Error("Could not load image library.");
  }
  return response.json();
}

export async function uploadImage(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/images`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? "Image upload failed.");
  }

  return response.json();
}

export async function searchImages(request: SearchRequest): Promise<SearchResult[]> {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? "Search failed.");
  }

  return response.json();
}

export async function createAnnotation(
  imageId: number,
  payload: { note: string; tags: string },
): Promise<Annotation> {
  const response = await fetch(`${API_BASE_URL}/annotations/${imageId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ...payload, created_by: "designer" }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail ?? "Could not save annotation.");
  }

  return response.json();
}
