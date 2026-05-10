"use client";

import { useCallback, useMemo, useState } from "react";
import { useDropzone } from "react-dropzone";
import { CheckCircle2, FileText, Loader2, UploadCloud, XCircle } from "lucide-react";
import type { UploadResumeResponse } from "@/types";

type UploadStatus = "pending" | "uploading" | "success" | "error";

interface FileUploadState {
  status: UploadStatus;
  message?: string;
}

const UPLOAD_ENDPOINT = "http://127.0.0.1:8000/upload-resume";

export default function UploadPage() {
  const [acceptedFiles, setAcceptedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [fileStates, setFileStates] = useState<Record<string, FileUploadState>>({});

  const onDrop = useCallback((files: File[]) => {
    setAcceptedFiles(files);
    const nextState: Record<string, FileUploadState> = {};
    files.forEach((file) => {
      nextState[file.name] = { status: "pending" };
    });
    setFileStates(nextState);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
    accept: {
      "application/pdf": [".pdf"],
    },
  });

  const statusSummary = useMemo(() => {
    const values = Object.values(fileStates);
    const successCount = values.filter((item) => item.status === "success").length;
    const errorCount = values.filter((item) => item.status === "error").length;
    return { successCount, errorCount };
  }, [fileStates]);

  const uploadAllFiles = async () => {
    if (acceptedFiles.length === 0 || uploading) {
      return;
    }

    setUploading(true);

    for (const file of acceptedFiles) {
      setFileStates((prev) => ({
        ...prev,
        [file.name]: { status: "uploading" },
      }));

      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(UPLOAD_ENDPOINT, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const body = (await response.json().catch(() => null)) as
            | { detail?: { message?: string } }
            | null;
          throw new Error(body?.detail?.message ?? "Upload failed.");
        }

        const data = (await response.json()) as UploadResumeResponse;
        setFileStates((prev) => ({
          ...prev,
          [file.name]: {
            status: "success",
            message: `Stored as ${data.database_id}`,
          },
        }));
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unexpected upload error.";
        setFileStates((prev) => ({
          ...prev,
          [file.name]: {
            status: "error",
            message,
          },
        }));
      }
    }

    setUploading(false);
  };

  return (
    <section className="space-y-6">
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Upload Resumes</h1>
        <p className="mt-1 text-sm text-slate-600">
          Drag and drop PDF resumes and upload them into the ATS vector database.
        </p>

        <div
          {...getRootProps()}
          className={`mt-5 cursor-pointer rounded-xl border-2 border-dashed p-10 text-center transition ${
            isDragActive
              ? "border-blue-500 bg-blue-50"
              : "border-slate-300 bg-slate-50 hover:border-slate-400"
          }`}
        >
          <input {...getInputProps()} />
          <UploadCloud className="mx-auto h-10 w-10 text-blue-600" />
          <p className="mt-3 text-sm font-medium text-slate-900">
            {isDragActive ? "Drop files here" : "Drop PDF resumes here or click to browse"}
          </p>
          <p className="mt-1 text-xs text-slate-500">Only .pdf files are accepted</p>
        </div>

        <div className="mt-5 flex items-center justify-between">
          <p className="text-sm text-slate-600">{acceptedFiles.length} file(s) selected</p>
          <button
            type="button"
            onClick={() => void uploadAllFiles()}
            disabled={uploading || acceptedFiles.length === 0}
            className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
          >
            {uploading ? "Uploading..." : "Upload to Database"}
          </button>
        </div>

        {acceptedFiles.length > 0 ? (
          <p className="mt-3 text-xs text-slate-500">
            Completed: {statusSummary.successCount} success, {statusSummary.errorCount} failed.
          </p>
        ) : null}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Selected Files</h2>

        {acceptedFiles.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">No files selected yet.</p>
        ) : (
          <ul className="mt-4 space-y-3">
            {acceptedFiles.map((file) => {
              const state = fileStates[file.name] ?? { status: "pending" as const };
              return (
                <li
                  key={file.name}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3"
                >
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-slate-500" />
                    <span className="text-sm font-medium text-slate-800">{file.name}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    {state.status === "uploading" ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        Uploading
                      </span>
                    ) : null}
                    {state.status === "success" ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        Success
                      </span>
                    ) : null}
                    {state.status === "error" ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700">
                        <XCircle className="h-3.5 w-3.5" />
                        Error
                      </span>
                    ) : null}
                    {state.status === "pending" ? (
                      <span className="rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold text-slate-700">
                        Pending
                      </span>
                    ) : null}
                  </div>

                  {state.message ? (
                    <p className="w-full text-xs text-slate-500">{state.message}</p>
                  ) : null}
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </section>
  );
}
