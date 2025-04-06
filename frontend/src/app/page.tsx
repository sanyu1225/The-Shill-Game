"use client";

import { Button } from "pixel-retroui";
import { useAccount, useConfig, useWriteContract, useReadContract } from "wagmi";
import { switchChain } from "@wagmi/core";
import { useConnectModal } from "@rainbow-me/rainbowkit";
import { useCallback, useState, useEffect } from "react";
import Header from "./_component/header";
import Stage from "./_component/stage";
import { CONTRACT_ADDRESS, CONTRACT_ABI } from "@/config/abi/NFT";
import { useWebSocket } from "@/context/WebSocketContext";

export default function Home() {
  const { isConnected, address } = useAccount();
  const config = useConfig();
  const { openConnectModal } = useConnectModal();
  const { writeContractAsync } = useWriteContract();
  const [hasNFT, setHasNFT] = useState(false);
  const { setup, messages, getGameState } = useWebSocket();
  const [gameState, setGameState] = useState<string|null>(null);
  // useEffect(() => {
  //   const fetchGameState = async () => {
  //     const gameState = await getGameState();
  //     if(gameState?.status === "not_initialized"){
  //       setGameState("not_initialized")
  //     }
  //   };
  //   fetchGameState();
  // }, []);
  
  const { data: balance } = useReadContract({
    address: CONTRACT_ADDRESS,
    abi: CONTRACT_ABI,
    functionName: 'balanceOf',
    args: address ? [address] : undefined,
    query: {
      enabled: !!address
    }
  });

  const { data: tokenId } = useReadContract({
    address: CONTRACT_ADDRESS,
    abi: CONTRACT_ABI,
    functionName: 'tokenOfOwnerByIndex',
    args: address ? [address, BigInt(0)] : undefined,
    query: {
      enabled: !!address && !!balance && Number(balance) > 0
    }
  });

  const { data: tokenURI } = useReadContract({
    address: CONTRACT_ADDRESS,
    abi: CONTRACT_ABI,
    functionName: 'tokenURI',
    args: tokenId !== undefined ? [tokenId] : undefined,
    query: {
      enabled: tokenId !== undefined
    }
  });
  useEffect(() => {
    if (tokenURI && typeof tokenURI === 'string') {
      const base64Data = tokenURI.replace("data:application/json;base64,", "");
      try {
        const decodedData = atob(base64Data);
        const nftData = JSON.parse(decodedData);
        
        const processedTraits = nftData.attributes.reduce((acc: Record<string, string>, trait: { trait_type: string; value: string }) => {
          const key = trait.trait_type.toLowerCase().replace(/\s+/g, '_');
          acc[key] = trait.value;
          return acc;
        }, {});

        if (Object.keys(processedTraits).length > 0) {
          console.log("messages",messages[0])
          const gameState = messages[0].content
          if(gameState === "not_initialized"){
            setup(processedTraits);
          }
        }
      } catch (error) {
        console.error("Error decoding base64 data:", error);
      }
    }
  }, [tokenURI, setup, messages, gameState]);

  useEffect(() => {
    if (balance && typeof balance === 'bigint' && balance > 0) {
      setHasNFT(true);
    }
  }, [balance]);

  const handleMint = async () => {
    try {
      const hash = await writeContractAsync({
        address: CONTRACT_ADDRESS,
        abi: CONTRACT_ABI,
        functionName: 'mint',
      });
      
      console.log('Mint transaction hash:', hash);
      setHasNFT(true);
    } catch (error) {
      console.error("Mint failed:", error);
      if (error instanceof Error) {
        console.error(`Mint failed: ${error.message}`);
      } else {
        console.error('Mint failed: Unknown error');
      }
    }
  };

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

  if (!isConnected) {
    return (
      <div className="bg-[#112a41] grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
        <main className="flex flex-col justify-center gap-[32px] row-start-2 items-center">
          <Button onClick={() => connectWallet()}>Connect Wallet</Button>
        </main>
      </div>
    );
  }

  if (!hasNFT) {
    return (
      <div className="bg-[#112a41] grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
        <main className="flex flex-col justify-center gap-[32px] row-start-2 items-center">
          <Header />
          <div className="mt-4 text-center">
            <div className="flex flex-col items-center gap-2">
              <p className="text-yellow-500">You don&apos;t have Shill Game NFT</p>
              <Button onClick={handleMint}>Get NFT</Button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header />
      <Stage />
    </div>
  );
}
