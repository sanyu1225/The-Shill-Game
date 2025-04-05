import type { Metadata } from "next";
import Provider from "./provider";
import "./globals.css";
import "pixel-retroui/dist/index.css";
import { WebSocketProvider } from "@/context/WebSocketContext";
import { CharacterProvider } from "@/context/CharacterContext";

export const metadata: Metadata = {
  title: "The Shill Game",
  description: "The Shill Game 🎮",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`antialiased font-minecraft`}>
        <WebSocketProvider>
          <CharacterProvider>
            <Provider>{children}</Provider>
          </CharacterProvider>
        </WebSocketProvider>
      </body>
    </html>
  );
}
