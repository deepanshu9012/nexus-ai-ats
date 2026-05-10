"use client";

import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const router = useRouter();
  const pathname = usePathname();
  const hideHeader = pathname === "/login" || pathname === "/register" || pathname === "/";

  const handleLogout = () => {
    document.cookie = "ats_auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    router.push("/");
  };

  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-[#0a0a0a] to-black text-slate-100 min-h-screen">
        <div className="min-h-screen flex flex-col">
          {!hideHeader ? (
            <header className="sticky top-0 z-50 border-b border-white/10 bg-black/40 backdrop-blur-md">
              <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-500/30">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="h-6 w-6"
                    >
                      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                      <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
                      <line x1="12" y1="22.08" x2="12" y2="12" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-400">Nexus AI</p>
                    <p className="text-base font-semibold tracking-tight text-white">
                      Talent Intelligence
                    </p>
                  </div>
                </div>
                <nav className="flex items-center gap-2 text-sm font-medium">
                  <Link
                    href="/dashboard"
                    className="rounded-md border border-white/10 bg-white/5 px-4 py-2 text-slate-300 transition hover:bg-white/10 hover:text-white"
                  >
                    AI Agent
                  </Link>
                  <Link
                    href="/dashboard/database"
                    className="rounded-md border border-white/10 bg-white/5 px-4 py-2 text-slate-300 transition hover:bg-white/10 hover:text-white"
                  >
                    Database
                  </Link>
                  <Link
                    href="/upload"
                    className="rounded-md border border-white/10 bg-white/5 px-4 py-2 text-slate-300 transition hover:bg-white/10 hover:text-white"
                  >
                    Upload Resumes
                  </Link>
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="rounded-md border border-white/10 bg-white/5 px-4 py-2 text-slate-300 transition hover:border-red-400/40 hover:bg-red-500/20 hover:text-red-300"
                  >
                    Logout
                  </button>
                </nav>
              </div>
            </header>
          ) : null}
          <main className="mx-auto w-full max-w-7xl flex-1 px-6 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
