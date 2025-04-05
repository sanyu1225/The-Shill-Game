"use client";

import Image from "next/image";
import { useState, useEffect } from "react";
import { useWebSocket } from "@/context/WebSocketContext";
import { Popup } from 'pixel-retroui';

interface GameState {
  status: string;
  round: number;
  round_phase: string;
  active_players: Array<{
    name: string;
    traits: Record<string, string>;
    memecoin: {
      name: string;
      symbol: string;
      backstory: string;
    };
  }>;
  eliminated_players: Array<{
    name: string;
    traits: Record<string, string>;
    memecoin: {
      name: string;
      symbol: string;
      backstory: string;
    };
  }>;
}

type Player = GameState['active_players'][0];

const GameStage = () => {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [thinkingPlayerId, setThinkingPlayerId] = useState<string | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const { messages, getGameState, getWinner } = useWebSocket();

  // 定时获取游戏状态
  useEffect(() => {
    const fetchGameState = async () => {
      const state = await getGameState();
      console.log("state", state);
      if (state) {
        if (state.round_phase === "game_over") {
          const winner = await getWinner();
          console.log("winner", winner);
        }
        setGameState(state);
      }
    };

    // 立即获取一次
    fetchGameState();

    // 每 2 秒获取一次
    const interval = setInterval(fetchGameState, 5000);

    return () => clearInterval(interval);
  }, [getGameState]);

  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];

      if (
        lastMessage.type === "agent" &&
        lastMessage.sender &&
        typeof lastMessage.sender === "string" &&
        !lastMessage.sender.includes("Host")
      ) {
        setThinkingPlayerId(lastMessage.sender);

        setTimeout(() => {
          setThinkingPlayerId(null);
        }, 4000);
      }
    }
  }, [messages]);

  return (
    <div className="relative w-[528px] h-[480px] overflow-hidden border-4 border-black">
      {/* 背景 */}
      <div
        className="absolute inset-0 w-full h-full bg-cover bg-center"
        style={{ backgroundImage: "url('/bg.png')" }}
      />

      {/* 角色群组容器 */}
      <div className="absolute bottom-20 right-20 flex gap-2 top-[40%] left-[28%]">
        {[1, 2, 3, 4, 5, 6].map((num, index) => {
          const isActive = gameState?.active_players?.[index];
          if (!isActive) return null;

          const playerAtThisPosition = gameState?.active_players?.[index];
          const isThinking = playerAtThisPosition?.name === thinkingPlayerId;

          return (
            <div 
              key={num} 
              className="relative cursor-pointer"
              onClick={() => {
                setSelectedPlayer(playerAtThisPosition);
                setIsPopupOpen(true);
              }}
            >
              {isThinking && (
                <Image
                  src="/thinking.gif"
                  width={20}
                  height={20}
                  className="absolute bottom-full left-1/2 -translate-x-1/2"
                  alt="thinking"
                />
              )}
              <div
                className="w-8 h-12 bg-no-repeat bg-center"
                style={{
                  backgroundImage: `url('/Characters/${num}.png')`,
                  backgroundSize: "128px 192px",
                  backgroundPosition: "0 0",
                }}
              />
            </div>
          );
        })}
      </div>

      <Popup
        isOpen={isPopupOpen}
        onClose={() => setIsPopupOpen(false)}
      >
        {selectedPlayer && (
          <div className="p-4">
            <h3 className="text-xl font-bold mb-4">{selectedPlayer.name}</h3>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(selectedPlayer.traits).map(([key, value]) => (
                <div key={key} className="mb-2">
                  <span className="font-medium capitalize">{key.replace(/_/g, ' ')}: </span>
                  <span>{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </Popup>
    </div>
  );
};

export default GameStage;
