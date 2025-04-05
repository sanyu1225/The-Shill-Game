"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useWebSocket } from './WebSocketContext';

interface Character {
  id: string;
  spriteIndex: number; // 1-6 for different character sprites
  position: {
    x: number;
    y: number;
  };
}

interface CharacterContextType {
  characters: Character[];
  addCharacter: (id: string) => void;
}

const CharacterContext = createContext<CharacterContextType | undefined>(undefined);

export function CharacterProvider({ children }: { children: React.ReactNode }) {
  const [characters, setCharacters] = useState<Character[]>([]);
  const { messages } = useWebSocket();

  // 舞台配置
  const STAGE = {
    PLATFORM_Y: 400,    // 调整到舞台底部
    START_X: 100,       // 更靠左一些
    SPACING: 100,       // 增加间距
    MAX_CHARACTERS: 3   // 最大角色数量
  };

  useEffect(() => {
    if (messages.length > 0) {
      const latestMessage = messages[messages.length - 1];
      if (latestMessage.type === 'agent' && latestMessage.sender) {
        addCharacter(latestMessage.sender);
      }
    }
  }, [messages]);

  const addCharacter = (id: string) => {
    setCharacters(prev => {
      // 如果角色已存在，不添加
      if (prev.find(char => char.id === id)) {
        return prev;
      }

      // 如果已达到最大角色数量，不添加
      if (prev.length >= STAGE.MAX_CHARACTERS) {
        return prev;
      }

      // 计算新角色的位置
      const index = prev.length;
      return [...prev, {
        id,
        spriteIndex: (index % 6) + 1,
        position: {
          x: STAGE.START_X + (index * STAGE.SPACING),
          y: STAGE.PLATFORM_Y
        }
      }];
    });
  };

  return (
    <CharacterContext.Provider value={{ characters, addCharacter }}>
      {children}
    </CharacterContext.Provider>
  );
}

export function useCharacters() {
  const context = useContext(CharacterContext);
  if (context === undefined) {
    throw new Error('useCharacters must be used within a CharacterProvider');
  }
  return context;
} 