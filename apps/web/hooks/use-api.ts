"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";

// ─── Certificates ─────────────────────────────────────────────────────────────
export function useCertificates(page = 1) {
  return useQuery({
    queryKey: ["certificates", page],
    queryFn: () => apiClient.get(`/certificates?page=${page}&page_size=20`).then(r => r.data),
  });
}

export function useGenerateCertificate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { shipment_id: string; determination_id: string; cert_type: string }) =>
      apiClient.post("/certificates/generate", data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["certificates"] }),
  });
}

// ─── BOM ──────────────────────────────────────────────────────────────────────
export function useBOMItems(productId: string | null) {
  return useQuery({
    queryKey: ["bom", productId],
    queryFn: () => apiClient.get(`/bom/${productId}/items`).then(r => r.data),
    enabled: !!productId,
  });
}

export function useUploadBOM() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ productId, file }: { productId: string; file: File }) => {
      const form = new FormData();
      form.append("file", file);
      return apiClient.post(`/bom/upload?product_id=${productId}`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      }).then(r => r.data);
    },
    onSuccess: (_, { productId }) => qc.invalidateQueries({ queryKey: ["bom", productId] }),
  });
}

// ─── Origin ───────────────────────────────────────────────────────────────────
export function useDetermination(determinationId: string | null) {
  return useQuery({
    queryKey: ["determination", determinationId],
    queryFn: () => apiClient.get(`/origin/${determinationId}`).then(r => r.data),
    enabled: !!determinationId,
    refetchInterval: (data: any) => data?.status === "queued" || data?.status === "processing" ? 2000 : false,
  });
}

export function useRunDetermination() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { shipment_id: string; agreement_codes: string[] }) =>
      apiClient.post("/origin/determine", data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["determination"] }),
  });
}

// ─── Agreements ───────────────────────────────────────────────────────────────
export function useAgreements(originCountry?: string, destinationCountry?: string) {
  return useQuery({
    queryKey: ["agreements", originCountry, destinationCountry],
    queryFn: () => {
      const params = new URLSearchParams();
      if (originCountry) params.set("origin_country", originCountry);
      if (destinationCountry) params.set("destination_country", destinationCountry);
      return apiClient.get(`/agreements?${params}`).then(r => r.data);
    },
  });
}

export function useClassifyHS() {
  return useMutation({
    mutationFn: (description: string) =>
      apiClient.post(`/agreements/classify-hs?description=${encodeURIComponent(description)}`).then(r => r.data),
  });
}
