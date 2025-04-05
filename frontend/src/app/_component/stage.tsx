"use client";

import { useWebSocket } from "@/context/WebSocketContext";
import { Button } from "pixel-retroui";
import MessageBoard from "./MessageBoard";
import GameStage from "./GameStage";
import { useState, useEffect } from "react";

const Stage = () => {
  const { startGame, nextRound, getGameState, messages } = useWebSocket();
  const [isRoundCompleted, setIsRoundCompleted] = useState(false);
  const [canStartGame, setCanStartGame] = useState(false);
  const [gameStarted, setGameStarted] = useState(false);

  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.type === 'system') {
        if (lastMessage.event === 'round_completed_ended') {
          setIsRoundCompleted(true);
        }
        // 当收到 Joined game 消息时，允许开始游戏
        if (lastMessage.content === 'Joined game.') {
          setCanStartGame(true);
          setGameStarted(false);
        }
      }
    }
  }, [messages]);

  const handleStartGame = async () => {
    console.log("🎮 Clicking Start Game button");
    await startGame();
    setGameStarted(true);
    setCanStartGame(false);
  };

  return (
    <>
      <div className="min-h-screen bg-[#1a1a2e] pt-16 p-8">
        <div className="max-w-[1200px] mx-auto grid grid-cols-[2fr_1fr] gap-8">
          <div className="space-y-6">
            <GameStage />
            
            <div className="flex justify-center gap-4">
              <Button 
                onClick={handleStartGame}
                className={`!min-w-[120px] !h-[45px] transition-all duration-300
                  ${canStartGame ? 'animate-pulse' : 'opacity-50 cursor-not-allowed'}
                `}
                disabled={!canStartGame || gameStarted}
              >
                Start Game
              </Button>
              <Button 
                onClick={() => {
                  console.log("🔄 Clicking Next Round button");
                  nextRound();
                  setIsRoundCompleted(false);
                }}
                className={`!min-w-[120px] !h-[45px] transition-all duration-300
                  ${isRoundCompleted ? 'animate-pulse' : 'opacity-50 cursor-not-allowed'}
                `}
                disabled={!isRoundCompleted}
              >
                Next Round
              </Button>
            </div>
          </div>

          <div>
            <MessageBoard />
          </div>
        </div>
      </div>

      <style jsx global>{`
        @keyframes pulse-border {
          0% {
            box-shadow: 0 0 0 0 rgba(204, 248, 220, 0.7);
          }
          70% {
            box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
          }
        }
        
        .animate-pulse {
          animation: pulse-border 2s infinite;
        }
      `}</style>
    </>
  );
};

export default Stage;
