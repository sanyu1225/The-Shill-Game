"use client";

import Image from "next/image";
import { useState, useEffect } from "react";
import { useWebSocket } from "@/context/WebSocketContext";
import { Popup, Card } from 'pixel-retroui';

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

interface WinnerResponse {
  status: string;
  winners?: Array<{
    name: string;
    memecoin: string;
    takeaway: string;
  }>;
  winner?: {
    name: string;
    memecoin: string;
    takeaway: string;
  };
}

interface WinnerInfo {
  name: string;
  memecoin: string;
  takeaway: string;
}

type Player = GameState['active_players'][0];

const GameStage = () => {
  const [thinkingPlayerId, setThinkingPlayerId] = useState<string | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const { messages, gameState, getWinner } = useWebSocket();
  const [showWinner, setShowWinner] = useState(false);
  const [winners, setWinners] = useState<WinnerInfo[]>([]);
  // const isMe = 
  const getWinnerHandler = async () => {
    const winner = await getWinner() as WinnerResponse | null;
    console.log("winner", winner);
    
    if (!winner) return;

    // Handle both response formats
    if ('winners' in winner && winner.winners) {
      // Handle array of winners
      setWinners(winner.winners);
    } else if ('winner' in winner && winner.winner) {
      // Handle single winner
      setWinners([winner.winner]);
    }
    setShowWinner(true);
  }
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
      // game_over_ended
      if(lastMessage.type === "system" && lastMessage.event === "game_over_ended"){
        // setShowWinner(true);
        getWinnerHandler();
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

      {/* Winner Card */}
      {showWinner && (
        <div className="absolute top-12 left-0 right-0 flex items-center justify-center">
          <Card className="w-[60%] py-4 text-center">
            <h2 className="text-2xl font-pixel mb-2">
              {winners.some(w => w.name === "Vitalik") ? "🎉 Congratulations! You Won! 🎉" : "🎮 Game Over 🎮"}
            </h2>
            {winners.map((winner, index) => (
              <div key={index} className="mb-2">
                <p className="text-xl font-pixel">Winner: {winner.name}</p>
                <p className="text-sm font-pixel">Takeaway: {winner.takeaway}</p>
              </div>
            ))}
          </Card>
        </div>
      )}

      {/* 角色群组容器 */}
      <div className="absolute bottom-20 right-15 flex gap-2 top-[40%] left-[28%]">
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
