import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { SnackbarProvider } from "@/components/providers/snackbarProvider";
import { AuthProvider } from "@/components/providers/authProvider";

const interSans = Inter({
  variable: "--font-inter-sans",
  subsets: ["latin"],
});


export const metadata: Metadata = {
  title: "Peralta Cobranças",
  description: "",
};

export default function RootLayout({children,}: Readonly<{children: React.ReactNode;}>) {  
  return (
    <html lang="en">
      <body
        className={`${interSans.variable} antialiased`}
      >
        <div className="bg-white font-inter">
          <SnackbarProvider>
            <AuthProvider>
              {children}
            </AuthProvider>
          </SnackbarProvider>
        </div>
      </body>
    </html>
  );
}
