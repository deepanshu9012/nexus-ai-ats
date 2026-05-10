"use client";

import { AnimatePresence, motion } from "framer-motion";
import type { CandidateProfile } from "@/types";

interface CandidateProfileWithDetails extends CandidateProfile {
  experience_details?: any;
}

interface CandidateModalProps {
  isOpen: boolean;
  onClose: () => void;
  candidate: CandidateProfileWithDetails | null;
}

export default function CandidateModal({
  isOpen,
  onClose,
  candidate,
}: CandidateModalProps) {
  const hasArrayDetails =
    Array.isArray(candidate?.experience_details) && candidate.experience_details.length > 0;
  const hasStringDetails =
    typeof candidate?.experience_details === "string" &&
    candidate.experience_details.trim().length > 0;

  return (
    <AnimatePresence>
      {isOpen && candidate ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.98 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="max-h-[70vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-white/10 bg-slate-950/80 p-6 shadow-2xl backdrop-blur-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-semibold text-white">{candidate.name}</h2>
                <p className="mt-1 text-sm text-slate-300">{candidate.email}</p>
                <p className="mt-2 text-sm text-slate-300">
                  <span className="font-semibold text-white">Education:</span>{" "}
                  {candidate.education}
                </p>
              </div>
              <div className="flex items-start gap-2">
                <span className="rounded-full border border-indigo-500/30 bg-indigo-500/20 px-3 py-1.5 text-xs font-semibold text-indigo-300">
                  {candidate.years_experience} years
                </span>
                <button
                  type="button"
                  onClick={onClose}
                  className="rounded-md border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-slate-300 transition hover:bg-white/10 hover:text-white"
                >
                  Close
                </button>
              </div>
            </div>

            <div className="mt-6">
              <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
                Skills
              </p>
              <div className="flex flex-wrap gap-2">
                {Array.from(new Set(candidate.skills)).map((skill, index) => (
                  <span
                    key={`${candidate.email}-${skill}-${index}`}
                    className="rounded-full border border-indigo-500/30 bg-indigo-500/20 px-3 py-1 text-xs font-semibold text-indigo-300"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-6">
              <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
                Detailed Work Experience
              </p>

              {hasStringDetails ? (
                <p className="whitespace-pre-wrap text-sm text-slate-300">
                  {candidate.experience_details}
                </p>
              ) : null}

              {hasArrayDetails ? (
                <div className="space-y-3">
                  {candidate.experience_details.map((job: any, index: number) => {
                    const role = job?.role || job?.title || "Role not specified";
                    const company = job?.company || job?.organization || "Company not specified";
                    const start = job?.start_date || job?.start || "N/A";
                    const end = job?.end_date || job?.end || "N/A";

                    return (
                      <div
                        key={`${role}-${company}-${index}`}
                        className="rounded-xl border border-white/10 bg-white/5 p-3"
                      >
                        <p className="text-sm font-semibold text-white">{role}</p>
                        <p className="text-sm text-slate-300">{company}</p>
                        <p className="mt-1 text-xs text-slate-400">
                          {start} - {end}
                        </p>
                      </div>
                    );
                  })}
                </div>
              ) : null}

              {!hasStringDetails && !hasArrayDetails ? (
                <p className="text-sm text-slate-400">
                  Detailed work history not available in parsed data.
                </p>
              ) : null}
            </div>
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
