'use client'

import { RainbowKitProvider, darkTheme } from '@rainbow-me/rainbowkit';
import { config } from "@/lib/wagmi";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WagmiProvider } from "wagmi";
import { WebSocketProvider } from '@/context/WebSocketContext';
import '@rainbow-me/rainbowkit/styles.css';

const queryClient = new QueryClient();

const Provider = ({ children }: { children: React.ReactNode }) => {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider theme={darkTheme()}>
          <WebSocketProvider>
            {children}
          </WebSocketProvider>
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
};

export default Provider;
