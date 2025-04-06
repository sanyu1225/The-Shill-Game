"use client";

import React, { createContext, useContext, useEffect, useState, useRef } from 'react';

interface Message {
  type: string;
  players?: Array<{
    id: string;
    position: number;
  }>;
  status?: 'waiting' | 'started' | 'ended';
  currentRound?: number;
  [key: string]: unknown;
}

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

interface Winner {
  name: string;
  memecoin: string;
  takeaway: string;
}

interface WinnerResponse {
  status: string;
  winners: Winner[];
}

interface WebSocketContextType {
  isConnected: boolean;
  messages: Message[];
  gameState: GameState | null;
  startGame: () => Promise<void>;
  nextRound: () => Promise<void>;
  getGameState: () => Promise<GameState | null>;
  getWinner: () => Promise<WinnerResponse | null>;
  setup: (traits: Record<string, string>) => Promise<unknown>;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);
const WS_URL = 'wss://bloggers-barnes-entities-order.trycloudflare.com/ws';
const API_URL = 'https://bloggers-barnes-entities-order.trycloudflare.com';

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [gameState, setGameState] = useState<GameState | null>(null);
  const socket = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  
  // 轮询游戏状态
  useEffect(() => {
    const fetchGameState = async () => {
      const state = await getGameState();
      if (state) {
        // if (state.round_phase === "game_over") {
        //   const winner = await getWinner();
        //   console.log("winner", winner);
        // }
        setGameState(state);
      }
    };

    // 立即获取一次
    fetchGameState();

    // 每 5 秒获取一次
    const interval = setInterval(fetchGameState, 5000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    socket.current = new WebSocket(WS_URL);

    socket.current.onopen = () => {
      console.log('WebSocket Connected');
      setIsConnected(true);
    };

    socket.current.onclose = () => {
      console.log('WebSocket Disconnected');
      setIsConnected(false);
    };

    socket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received message:', data);
      setMessages(prev => [...prev, data]);
    };

    return () => {
      if (socket.current) {
        socket.current.close();
      }
    };
  }, []);

  const startGame = async () => {
    try {
      const response = await fetch(`${API_URL}/game/start`, {
        method: "POST",
      });
      const data = await response.json();
      console.log("📤 Start game result:", data);
    } catch (error) {
      console.error("❌ Error starting game:", error);
    }
  };

  const nextRound = async () => {
    try {
      const response = await fetch(`${API_URL}/game/next-round`, {
        method: "POST",
      });
      const data = await response.json();
      console.log("📤 Next round result:", data);
    } catch (error) {
      console.error("❌ Error triggering next round:", error);
    }
  };

  const getGameState = async () => {
    try {
      const response = await fetch(`${API_URL}/game/state`);
      const data = await response.json();
      console.log("📊 Game state:", data);
      return data;
    } catch (error) {
      console.error("❌ Error fetching game state:", error);
      return null;
    }
  };

  const getWinner = async () => {
    try {
      const response = await fetch(`${API_URL}/game/winner`);
      const data = await response.json();
      console.log("🏆 Winner result:", data);
      return data;
    } catch (error) {
      console.error("❌ Error fetching winner:", error);
      return null;
    }
  };

  const setup = async (traits: Record<string, string>) => {
    try {
      const response = await fetch(`${API_URL}/game/setup`, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(traits),
      });
      const data = await response.json();
      console.log("🎮 Setup result:", data);
      return data;
    } catch (error) {
      console.error("❌ Error in setup:", error);
      return null;
    }
  };

  return (
    <WebSocketContext.Provider value={{
      isConnected,
      messages,
      gameState,
      startGame,
      nextRound,
      getGameState,
      getWinner,
      setup,
    }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
} 