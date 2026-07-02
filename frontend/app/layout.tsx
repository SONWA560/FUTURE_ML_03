import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ScreeningProvider } from "@/lib/screening-context";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Resume Screening & Ranking",
  description: "Screen, score and rank candidate resumes against a job role using NLP.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en-GB"
      className={`dark ${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <ScreeningProvider>{children}</ScreeningProvider>
      </body>
    </html>
  );
}
