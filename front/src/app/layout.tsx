import "./globals.css";
import { Inter } from "next/font/google";
import type { Metadata } from "next";
import { AllProviders } from "@/components/providers/allProviders";

const interSans = Inter({
  variable: "--font-inter-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Peralta Cobranças",
  description: "",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${interSans.variable} antialiased`}>
        <div className="bg-white font-inter overflow-y-scroll">
          <AllProviders>
            {children}
          </AllProviders>
        </div>
      </body>
    </html>
  );
}
