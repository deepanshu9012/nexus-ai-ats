"use client";

import Link from "next/link";
import { motion } from "framer-motion";

export default function LandingPage() {
  return (
    <section className="relative flex min-h-[calc(100vh-6rem)] items-center justify-center overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-28 left-1/2 h-80 w-80 -translate-x-[60%] rounded-full bg-indigo-500/30 blur-3xl" />
        <div className="absolute right-[-6rem] top-1/3 h-72 w-72 rounded-full bg-fuchsia-400/20 blur-3xl" />
        <div className="absolute bottom-[-8rem] left-[-4rem] h-80 w-80 rounded-full bg-cyan-400/20 blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative mx-auto max-w-4xl rounded-3xl border border-white/10 bg-black/40 px-6 py-14 text-center shadow-2xl backdrop-blur-2xl"
      >
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.5, ease: "easeOut" }}
          className="text-sm font-semibold uppercase text-indigo-400 tracking-widest"
        >
          Enterprise ATS
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.55, ease: "easeOut" }}
          className="mt-4 text-4xl font-semibold tracking-tight text-white sm:text-5xl"
        >
          Next-Generation Talent Intelligence
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.55, ease: "easeOut" }}
          className="mx-auto mt-5 max-w-2xl text-lg text-slate-300"
        >
          AI-powered resume parsing, semantic search, and automated candidate matching.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.55, ease: "easeOut" }}
          className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row"
        >
          <motion.div whileHover={{ scale: 1.05 }} transition={{ type: "spring", stiffness: 250 }}>
            <Link
              href="/login"
              className="inline-flex items-center justify-center rounded-lg border-none bg-indigo-600 px-6 py-3 text-sm font-medium text-white shadow-[0_0_15px_rgba(79,70,229,0.5)] transition hover:bg-indigo-500"
            >
              Login to ATS
            </Link>
          </motion.div>
          <motion.div whileHover={{ scale: 1.05 }} transition={{ type: "spring", stiffness: 250 }}>
            <Link
              href="/register"
              className="inline-flex items-center justify-center rounded-lg border border-white/10 bg-white/5 px-6 py-3 text-sm font-medium text-white transition hover:bg-white/10"
            >
              Request Access
            </Link>
          </motion.div>
        </motion.div>
      </motion.div>
    </section>
  );
}

