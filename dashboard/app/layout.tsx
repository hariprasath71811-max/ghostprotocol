import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GhostProtocol — Threat Crypt",
  description:
    "A Halloween-themed cloud security cockpit for zombie credentials, phishing lures, and safe threat triage.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
