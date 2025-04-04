"use client";

import { Button } from "pixel-retroui";
import { useAccount, useConfig } from "wagmi";
import { switchChain } from "@wagmi/core";
import { useConnectModal } from "@rainbow-me/rainbowkit";
import { useCallback, useState } from "react";
import Header from "./_component/header";

export default function Home() {
  const { isConnected } = useAccount();
  const config = useConfig();
  const { openConnectModal } = useConnectModal();

  const connectWallet = useCallback(
    async ({
      chainId,
    }: {
      chainId?: (typeof config)["chains"][number]["id"];
    } = {}) => {
      try {
        if (chainId) {
          await switchChain(config, { chainId });
        }
        openConnectModal?.();
      } catch (error) {
        console.error(error);
      }
    },
    [config, openConnectModal]
  );
  const [checkMint, setCheckMint] = useState(false);

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col justify-center gap-[32px] row-start-2 items-center sm:items-start">
        <div>
          {isConnected ? (
            <>
              <Header />
              <div>
                <p>Welcome</p>
              </div>
            </>
          ) : (
            <div>
              <div>
                <Button onClick={() => connectWallet()}>Connect Wallet</Button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
