import { celoAlfajores } from "wagmi/chains";
import { getDefaultConfig } from "@rainbow-me/rainbowkit";

export const config = getDefaultConfig({
  appName: "AI Agent Game",
  projectId: "YOUR_PROJECT_ID",
  chains: [celoAlfajores],
  ssr: true, // If your dApp uses server side rendering (SSR)
});
