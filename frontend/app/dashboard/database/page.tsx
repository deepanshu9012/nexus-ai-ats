"use client";

import { useEffect, useMemo, useState } from "react";
import { Eye, Trash2 } from "lucide-react";
import CandidateModal from "@/components/CandidateModal";
import type { CandidateProfile } from "@/types";

interface CandidateRow {
  id: string | number;
  profile: CandidateProfile;
}

const CANDIDATES_ENDPOINT = "http://127.0.0.1:8000/api/candidates";

export default function MasterControlRoomPage() {
  const [candidates, setCandidates] = useState<CandidateRow[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const selectedSet = useMemo(() => new Set(selectedIds), [selectedIds]);

  const filteredCandidates = useMemo(() => {
    const terms = searchTerm
      .split(",")
      .map((term) => term.trim().toLowerCase())
      .filter(Boolean);

    if (terms.length === 0) {
      return candidates;
    }

    return candidates.filter((candidate) => {
      const profile = candidate.profile;
      const name = (profile.name || "").toLowerCase();
      const email = (profile.email || "").toLowerCase();
      const skills = (profile.skills || []).map((skill) => skill.toLowerCase());

      return terms.every(
        (term) =>
          name.includes(term) ||
          email.includes(term) ||
          skills.some((skill) => skill.includes(term))
      );
    });
  }, [candidates, searchTerm]);

  const loadCandidates = async () => {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(CANDIDATES_ENDPOINT);
      if (!response.ok) {
        throw new Error("Failed to fetch candidate database.");
      }

      const data = (await response.json()) as CandidateRow[];
      setCandidates(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch candidate database.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadCandidates();
  }, []);

  const toggleSelection = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((existingId) => existingId !== id) : [...prev, id]
    );
  };

  const handleDeleteSelected = async () => {
    if (selectedIds.length === 0) {
      return;
    }

    setError("");

    try {
      const response = await fetch(CANDIDATES_ENDPOINT, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ids: selectedIds }),
      });

      if (!response.ok) {
        throw new Error("Failed to delete selected candidates.");
      }

      setCandidates((prev) => prev.filter((candidate) => !selectedSet.has(String(candidate.id))));
      setSelectedIds([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete selected candidates.");
    }
  };

  const handleDeleteOne = async (id: string) => {
    setError("");

    try {
      const response = await fetch(CANDIDATES_ENDPOINT, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ids: [id] }),
      });

      if (!response.ok) {
        throw new Error("Failed to delete candidate.");
      }

      setCandidates((prev) => prev.filter((candidate) => String(candidate.id) !== id));
      setSelectedIds((prev) => prev.filter((existingId) => existingId !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete candidate.");
    }
  };

  const handleDeleteAll = async () => {
    setError("");

    try {
      const response = await fetch(`${CANDIDATES_ENDPOINT}/all`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete all candidates.");
      }

      setCandidates([]);
      setSelectedIds([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete all candidates.");
    }
  };

  return (
    <section className="relative min-h-[calc(100vh-4rem)] w-full overflow-hidden">
      <div className="pointer-events-none fixed inset-0 z-[-1]">
        <div className="absolute -top-28 left-1/2 h-80 w-80 -translate-x-[60%] rounded-full bg-indigo-500/30 blur-3xl" />
        <div className="absolute right-[-6rem] top-1/3 h-72 w-72 rounded-full bg-fuchsia-400/20 blur-3xl" />
        <div className="absolute bottom-[-8rem] left-[-4rem] h-80 w-80 rounded-full bg-cyan-400/20 blur-3xl" />
      </div>

      <div className="space-y-6">
        <div className="rounded-2xl border border-white/10 bg-black/40 p-6 shadow-2xl backdrop-blur-lg">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="flex items-center">
                <h1 className="text-2xl font-bold tracking-tight text-white">Candidate Database</h1>
                <span className="ml-4 rounded-full border border-indigo-500/30 bg-indigo-500/20 px-3 py-1 text-sm font-medium text-indigo-300">
                  Total: {candidates.length}
                </span>
              </div>
              <p className="mt-1 text-sm text-slate-300">
                Master Control Room for searching, reviewing, and managing candidates.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => void handleDeleteSelected()}
                disabled={selectedIds.length === 0}
                className="rounded-lg border border-red-500/30 bg-red-500/20 px-4 py-2 text-sm font-medium text-red-400 transition hover:bg-red-500/30 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Delete Selected
              </button>
              <button
                type="button"
                onClick={() => void handleDeleteAll()}
                className="rounded-lg border border-red-500/30 bg-red-500/20 px-4 py-2 text-sm font-medium text-red-400 transition hover:bg-red-500/30"
              >
                Delete All
              </button>
            </div>
          </div>

          <div className="mt-5">
            <input
              type="text"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search by Name, Email, or Skill..."
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-base text-white placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            />
          </div>

          {error ? <p className="mt-3 text-sm text-red-400">{error}</p> : null}
        </div>

        <div className="overflow-x-auto rounded-2xl border border-white/10 bg-black/40 shadow-2xl backdrop-blur-lg">
          <table className="w-full border-collapse text-left">
            <thead className="border-b border-white/10 bg-white/5 text-xs uppercase tracking-wide text-slate-400">
              <tr>
                <th className="px-4 py-3">Select</th>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Experience</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="text-sm text-slate-300">
              {filteredCandidates.map((candidate) => {
                const id = String(candidate.id);
                const profile = candidate.profile;

                return (
                  <tr key={id} className="border-b border-white/5 hover:bg-white/5">
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        checked={selectedSet.has(id)}
                        onChange={() => toggleSelection(id)}
                        className="h-4 w-4 rounded border-white/20 bg-white/5 text-indigo-500 focus:ring-indigo-500"
                      />
                    </td>
                    <td className="px-4 py-3 font-medium text-white">{profile.name}</td>
                    <td className="px-4 py-3">{profile.email}</td>
                    <td className="px-4 py-3">{profile.years_experience} years</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => setSelectedCandidate(profile)}
                          className="inline-flex items-center gap-1 rounded-md border border-white/10 bg-white/5 px-2.5 py-1.5 text-xs font-medium text-slate-200 transition hover:bg-white/10 hover:text-white"
                        >
                          <Eye className="h-3.5 w-3.5" />
                          View Profile
                        </button>
                        <button
                          type="button"
                          onClick={() => void handleDeleteOne(id)}
                          className="inline-flex items-center gap-1 rounded-md border border-red-500/30 bg-red-500/20 px-2.5 py-1.5 text-xs font-medium text-red-400 transition hover:bg-red-500/30"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}

              {!isLoading && filteredCandidates.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-10 text-center text-sm text-slate-400">
                    No candidates match the current search criteria.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>

      <CandidateModal
        isOpen={!!selectedCandidate}
        onClose={() => setSelectedCandidate(null)}
        candidate={selectedCandidate}
      />
    </section>
  );
}
