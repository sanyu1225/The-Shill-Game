"use client";

import Image from "next/image";
import { useState, useEffect } from "react";
import { useWebSocket } from "@/context/WebSocketContext";

interface GameState {
  status: string;
  round: number;
  round_phase: string;
  active_players: Array<{
    name: string;
    traits: Record<string, string>;
    memecoin: string;
  }>;
  eliminated_players: Array<{
    name: string;
    traits: Record<string, string>;
    memecoin: string;
  }>;
}

const GameStage = () => {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [thinkingPlayerId, setThinkingPlayerId] = useState<string | null>(null);
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

  // 处理消息，设置正在思考的角色
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];

      if (
        lastMessage.type === "agent" &&
        lastMessage.sender &&
        !lastMessage.sender.includes("Host")
      ) {
        setThinkingPlayerId(lastMessage.sender);

        // 4秒后清除思考状态
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
          // 检查这个位置是否有活跃的玩家
          const isActive = gameState?.active_players?.[index];

          // 如果没有活跃的玩家在这个位置，不显示角色
          if (!isActive) return null;

          // 检查这个位置的玩家是否正在思考
          const playerAtThisPosition = gameState?.active_players?.[index];
          const isThinking = playerAtThisPosition?.name === thinkingPlayerId;

          return (
            <div key={num} className="relative">
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
    </div>
  );
};

export default GameStage;
