import type { Metadata, Viewport } from "next";
import { Archivo } from "next/font/google";

import "./globals.css";

const archivo = Archivo({
  subsets: ["latin"],
  axes: ["wdth"],
  variable: "--font-archivo",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Truco Bot",
  description: "Truco argentino 1 vs 1 contra bots que muestran cómo deciden.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#1e4d3b",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es-AR" className={archivo.variable}>
      <body>{children}</body>
    </html>
  );
}
