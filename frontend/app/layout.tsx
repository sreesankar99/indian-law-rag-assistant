import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Indian Law Assistant",
  description: "Search Indian Law",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}