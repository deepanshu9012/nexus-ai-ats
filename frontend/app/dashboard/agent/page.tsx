"use client";

import { FormEvent, useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";

const AGENT_ENDPOINT = "http://127.0.0.1:8000/api/agent/screen";

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
  const [evaluation, setEvaluation] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  // Create a reference to the text area so we can perfectly control its height
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // This effect auto-resizes the text box whenever the job description changes
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "150px"; // Reset to min-height first
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = scrollHeight + "px";
    }
  }, [jobDescription]);

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
        body: JSON.stringify({ job_description: jobDescription.trim() }),
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
    <section className="relative min-h-[calc(100vh-4rem)] w-full overflow-hidden bg-slate-50">
      <div className="pointer-events-none fixed inset-0 z-[-1]">
        <div className="absolute -top-28 left-1/2 h-80 w-80 -translate-x-[60%] rounded-full bg-blue-400/30 blur-3xl" />
        <div className="absolute right-[-6rem] top-1/3 h-72 w-72 rounded-full bg-cyan-300/25 blur-3xl" />
        <div className="absolute bottom-[-8rem] left-[-4rem] h-80 w-80 rounded-full bg-indigo-300/25 blur-3xl" />
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="space-y-6"
      >
        <motion.div
          variants={itemVariants}
          className="rounded-2xl border border-white/50 bg-white/80 p-8 shadow-xl backdrop-blur-xl"
        >
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Hiring Screen Agent</h1>
          <p className="mt-1 text-sm text-slate-600">
            Paste a Job Description and let the AI agent search your resume database and write
            a structured hiring recommendation.
          </p>

          <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
            <textarea
              ref={textareaRef}
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder="Paste job description here..."
              className="min-h-[150px] w-full resize-none overflow-hidden rounded-xl border border-white/60 bg-white/90 px-4 py-3 text-sm text-slate-900 shadow-inner shadow-slate-200/70 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            />

            {error ? <p className="text-sm text-red-600">{error}</p> : null}

            <motion.button
              whileHover={{ scale: 1.04 }}
              transition={{ type: "spring", stiffness: 240 }}
              type="submit"
              disabled={isLoading}
              className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-3 text-sm font-medium text-white shadow-lg shadow-blue-500/25 transition hover:from-blue-700 hover:to-indigo-700 disabled:cursor-not-allowed disabled:from-blue-400 disabled:to-indigo-400"
            >
              {isLoading ? "Agent is analyzing..." : "Run AI Screen"}
            </motion.button>
          </form>
        </motion.div>

        {evaluation ? (
          <motion.div
            variants={itemVariants}
            className="rounded-2xl border border-white/50 bg-white/80 p-8 shadow-xl backdrop-blur-xl"
          >
            <h2 className="text-lg font-semibold text-slate-900">Evaluation Report</h2>
            {/* Bulletproof Markdown Styling Container */}
            <div className="mt-4 max-w-none text-slate-700 space-y-4 [&>h1]:text-2xl [&>h1]:font-bold [&>h1]:text-slate-900 [&>h2]:text-xl [&>h2]:font-bold [&>h2]:text-slate-900 [&>h3]:text-lg [&>h3]:font-bold [&>h3]:text-slate-900 [&>p]:leading-relaxed [&>ul]:list-disc [&>ul]:pl-5 [&>ul>li]:mb-1 [&>strong]:font-semibold [&>strong]:text-slate-900">
              <ReactMarkdown>{evaluation}</ReactMarkdown>
            </div>
          </motion.div>
        ) : null}
      </motion.div>
    </section>
  );
}