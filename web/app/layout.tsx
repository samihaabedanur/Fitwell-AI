import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Fitwell · find every material",
  description: "Upload a mood board or a material photo. Fitwell finds every material, similar real materials and their passports.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="top">
          <div className="wrap">
            <Link href="/" className="brand">FITWELL</Link>
            <nav className="links">
              <Link href="/moodboard">Mood board</Link>
              <Link href="/material">Single material</Link>
              <Link href="/planner">3D studio</Link>
            </nav>
          </div>
        </header>
        <main className="wrap">{children}</main>
        <footer>
          <div className="wrap">
            Library: 3,246 CC0 materials from MatSynth. Model trained with MINC-2500 (CC BY 4.0, Bell et al. 2015).
            Matches are suggestions; check samples before you specify.
          </div>
        </footer>
      </body>
    </html>
  );
}
