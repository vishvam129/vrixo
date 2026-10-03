import type { Metadata } from "next";
import { Barlow_Condensed, Schibsted_Grotesk } from "next/font/google";
import { Toaster } from "sonner";
import "./globals.css";

// Barlow Condensed echoes the edge print on film stock; Schibsted Grotesk does the reading.
const display = Barlow_Condensed({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});
const body = Schibsted_Grotesk({ variable: "--font-body", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Vrixo — fix a photo in one step",
  description:
    "Remove a background, upscale, restore faces, repair an old print, or take an object out of a photo.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable} h-full antialiased`}>
      <body className="min-h-full">
        {children}
        <Toaster
          position="bottom-center"
          toastOptions={{
            style: {
              background: "var(--ink)",
              color: "var(--surface)",
              border: "none",
              borderRadius: "4px",
              fontFamily: "var(--font-body)",
            },
          }}
        />
      </body>
    </html>
  );
}
