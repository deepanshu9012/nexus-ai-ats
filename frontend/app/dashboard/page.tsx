"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import CandidateModal from "@/components/CandidateModal";
import type { CandidateProfile } from "@/types";

const AGENT_ENDPOINT = "http://127.0.0.1:8000/api/agent/screen";
const CANDIDATES_ENDPOINT = "http://127.0.0.1:8000/api/candidates";

interface CandidateRow {
  id: string | number;
  profile: CandidateProfile;
}

const containerVariants = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.04,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 18 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, ease: "easeOut" },
  },
};

export default function HiringAgentPage() {
  const [jobDescription, setJobDescription] = useState("");
  const [numCandidates, setNumCandidates] = useState(3);
  const [evaluation, setEvaluation] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [candidates, setCandidates] = useState<CandidateRow[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateProfile | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "150px";
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${scrollHeight}px`;
    }
  }, [jobDescription]);

  useEffect(() => {
    const loadCandidates = async () => {
      try {
        const response = await fetch(CANDIDATES_ENDPOINT);
        if (!response.ok) {
          return;
        }
        const data = (await response.json()) as CandidateRow[];
        setCandidates(Array.isArray(data) ? data : []);
      } catch {
        setCandidates([]);
      }
    };

    void loadCandidates();
  }, []);

  const mentionedCandidates = useMemo(() => {
    if (!evaluation.trim()) {
      return [];
    }

    const agentReport = evaluation;

    // 1. Find all candidates whose name appears in the report
    let matched = candidates.filter((candidate) => {
      const name = candidate.profile?.name?.trim() ?? "";
      return Boolean(name) && agentReport.includes(name);
    });

    // 2. Remove candidates whose name is just a substring of another matched candidate's name
    matched = matched.filter((candidate) => {
      const candidateName = candidate.profile?.name?.trim() ?? "";
      const isSubstringOfAnother = matched.some((other) => {
        const otherName = other.profile?.name?.trim() ?? "";
        return otherName !== candidateName && otherName.includes(candidateName);
      });
      return !isSubstringOfAnother;
    });

    // 3. Deduplicate by email (fallback to id) to ensure no duplicate buttons render
    const uniqueMentionedCandidates = Array.from(
      new Map(
        matched.map((candidate) => [
          candidate.profile?.email?.trim() || String(candidate.id),
          candidate,
        ])
      ).values()
    );

    return uniqueMentionedCandidates;
  }, [candidates, evaluation]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!jobDescription.trim()) {
      setError("Please paste a job description before running the agent.");
      setEvaluation("");
      return;
    }

    setError("");
    setIsLoading(true);

    try {
      const response = await fetch(AGENT_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_description: jobDescription.trim(),
          num_candidates: numCandidates,
        }),
      });

      if (!response.ok) {
        const body = (await response.json().catch(() => null)) as
          | { detail?: string | { message?: string } }
          | null;
        const message =
          typeof body?.detail === "string"
            ? body.detail
            : body?.detail?.message ?? "Failed to run hiring screen agent.";
        throw new Error(message);
      }

      const data = (await response.json()) as { evaluation: string };
      setEvaluation(data.evaluation ?? "");
    } catch (err) {
      setEvaluation("");
      setError(err instanceof Error ? err.message : "Failed to run hiring screen agent.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="relative min-h-[calc(100vh-4rem)] w-full overflow-hidden">
      <div className="pointer-events-none fixed inset-0 z-[-1]">
        <div className="absolute -top-28 left-1/2 h-80 w-80 -translate-x-[60%] rounded-full bg-indigo-500/30 blur-3xl" />
        <div className="absolute right-[-6rem] top-1/3 h-72 w-72 rounded-full bg-fuchsia-400/20 blur-3xl" />
        <div className="absolute bottom-[-8rem] left-[-4rem] h-80 w-80 rounded-full bg-cyan-400/20 blur-3xl" />
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="space-y-6"
      >
        <motion.div
          variants={itemVariants}
          className="rounded-2xl border border-white/10 bg-black/40 p-8 shadow-2xl backdrop-blur-lg"
        >
          <h1 className="text-2xl font-bold tracking-tight text-white">Hiring Screen Agent</h1>
          <p className="mt-1 text-sm text-slate-300">
            Paste a Job Description and let the AI agent search your resume database and write
            a structured hiring recommendation.
          </p>

          <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
            <div className="max-w-xs">
              <label
                htmlFor="num-candidates"
                className="mb-1.5 block text-sm font-medium text-slate-300"
              >
                Number of Candidates to Shortlist
              </label>
              <input
                id="num-candidates"
                type="number"
                min={1}
                value={numCandidates}
                onChange={(event) => {
                  const parsed = Number.parseInt(event.target.value, 10);
                  setNumCandidates(Number.isNaN(parsed) || parsed < 1 ? 1 : parsed);
                }}
                className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              />
            </div>

            <textarea
              ref={textareaRef}
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder="Paste job description here..."
              className="min-h-[150px] w-full resize-none overflow-hidden rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white shadow-inner shadow-black/30 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            />

            {error ? <p className="text-sm text-red-400">{error}</p> : null}

            <motion.button
              whileHover={{ scale: 1.04 }}
              transition={{ type: "spring", stiffness: 240 }}
              type="submit"
              disabled={isLoading}
              className="inline-flex items-center justify-center rounded-xl bg-indigo-600 px-6 py-3 text-sm font-medium text-white shadow-[0_0_15px_rgba(79,70,229,0.5)] transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-indigo-400"
            >
              {isLoading ? "Agent is analyzing..." : "Run AI Screen"}
            </motion.button>
          </form>
        </motion.div>

        {evaluation ? (
          <motion.div
            variants={itemVariants}
            className="rounded-2xl border border-white/10 bg-black/40 p-8 shadow-2xl backdrop-blur-lg text-slate-300"
          >
            <h2 className="text-lg font-bold text-white">Evaluation Report</h2>
            <div className="agent-report prose prose-slate mt-4 max-w-none prose-headings:text-white prose-p:text-slate-300 prose-strong:text-white prose-li:text-slate-300 prose-a:text-indigo-300 dark:prose-invert [&_blockquote]:my-4 [&_blockquote]:rounded-r-lg [&_blockquote]:border-l-4 [&_blockquote]:border-indigo-500 [&_blockquote]:bg-indigo-500/10 [&_blockquote]:p-4 [&_blockquote]:text-indigo-100 [&_blockquote]:shadow-[0_0_15px_rgba(79,70,229,0.1)] [&_blockquote]:transition-all [&_blockquote]:duration-500 hover:[&_blockquote]:shadow-[0_0_25px_rgba(79,70,229,0.3)]">
              <ReactMarkdown>{evaluation}</ReactMarkdown>
            </div>

            <div className="mt-6">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-300">
                Evaluated Candidates:
              </h3>
              <div className="mt-3 flex flex-wrap gap-2">
                {mentionedCandidates.map((candidate) => (
                  <button
                    key={String(candidate.id)}
                    type="button"
                    onClick={() => setSelectedCandidate(candidate.profile)}
                    className="rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-white transition-all hover:bg-white/20"
                  >
                    View {candidate.profile.name}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        ) : null}
      </motion.div>

      <CandidateModal
        isOpen={!!selectedCandidate}
        onClose={() => setSelectedCandidate(null)}
        candidate={selectedCandidate}
      />
    </section>
  );
}
