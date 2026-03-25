"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, File, X, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";

interface FileDropzoneProps {
  onUpload: (file: File) => Promise<void>;
  accept?: Record<string, string[]>;
  maxSizeMB?: number;
  label?: string;
  hint?: string;
}

type UploadState = "idle" | "uploading" | "success" | "error";

export function FileDropzone({
  onUpload,
  accept = {
    "text/csv": [".csv"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    "application/vnd.ms-excel": [".xls"],
    "application/json": [".json"],
  },
  maxSizeMB = 10,
  label = "Drop your BOM file here",
  hint = "CSV, Excel (.xlsx), or JSON · Max 10 MB",
}: FileDropzoneProps) {
  const [state, setState] = useState<UploadState>("idle");
  const [fileName, setFileName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (accepted: File[], rejected: any[]) => {
      if (rejected.length > 0) {
        setError(rejected[0]?.errors?.[0]?.message || "File not accepted");
        return;
      }
      const file = accepted[0];
      if (!file) return;
      setFileName(file.name);
      setState("uploading");
      setError(null);
      try {
        await onUpload(file);
        setState("success");
      } catch (err: any) {
        setState("error");
        setError(err?.response?.data?.detail || "Upload failed");
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxFiles: 1,
    maxSize: maxSizeMB * 1024 * 1024,
  });

  const reset = () => { setState("idle"); setFileName(null); setError(null); };

  return (
    <div className="space-y-2">
      <div
        {...getRootProps()}
        className={cn(
          "relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-10 text-center transition-colors cursor-pointer",
          isDragActive           ? "border-brand-400 bg-brand-50"   : "border-slate-300 bg-slate-50 hover:border-brand-300 hover:bg-brand-50/50",
          state === "success"    ? "border-green-400 bg-green-50"   : "",
          state === "error"      ? "border-red-400 bg-red-50"       : "",
        )}
      >
        <input {...getInputProps()} />

        {state === "uploading" && (
          <div className="flex flex-col items-center gap-3">
            <Spinner className="h-8 w-8" />
            <p className="text-sm font-medium text-slate-600">Uploading & processing <span className="text-brand-600">{fileName}</span>…</p>
          </div>
        )}

        {state === "success" && (
          <div className="flex flex-col items-center gap-3">
            <CheckCircle2 className="h-10 w-10 text-green-500" />
            <p className="text-sm font-medium text-green-700">{fileName} uploaded successfully</p>
            <Button variant="outline" size="sm" onClick={(e) => { e.stopPropagation(); reset(); }}>
              Upload another file
            </Button>
          </div>
        )}

        {state === "idle" && (
          <>
            <div className="mb-4 rounded-full bg-brand-100 p-3">
              <Upload className="h-6 w-6 text-brand-600" />
            </div>
            <p className="text-sm font-semibold text-slate-700">{label}</p>
            <p className="mt-1 text-xs text-slate-400">{hint}</p>
            <Button variant="outline" size="sm" className="mt-4" onClick={(e) => e.stopPropagation()}>
              Browse files
            </Button>
          </>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          <X className="h-4 w-4 shrink-0" />
          {error}
          <button className="ml-auto text-red-400 hover:text-red-600" onClick={reset}>Dismiss</button>
        </div>
      )}
    </div>
  );
}
