import type { Metadata } from "next";
import { Jost } from "next/font/google";
import Providers from "@/shared/api/Providers";
import "@/styles/globals.css";

const jost = Jost({
  subsets: ["latin"],
  variable: "--font-jost",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Beauty Studio",
  description: "Book your appointment at Beauty Studio",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt" className={jost.variable}>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
