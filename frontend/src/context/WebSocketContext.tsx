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
  [key: string]: any;
}

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
  startGame: () => Promise<void>;
  nextRound: () => Promise<void>;
  getGameState: () => Promise<GameState | null>;
  getWinner: () => Promise<WinnerResponse | null>;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

const WS_URL = 'ws://54.252.233.89:8000/ws';
const API_URL = 'http://54.252.233.89:8000';

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const socket = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 5000;

  useEffect(() => {
    // 连接 WebSocket
    socket.current = new WebSocket(WS_URL);

    socket.current.onopen = () => {
      console.log('WebSocket Connected');
      setIsConnected(true);
      setReconnectAttempts(0);
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

  return (
    <WebSocketContext.Provider value={{
      isConnected,
      messages,
      startGame,
      nextRound,
      getGameState,
      getWinner,
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