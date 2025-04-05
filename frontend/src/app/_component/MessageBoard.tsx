"use client";

import { Card } from 'pixel-retroui';
import { useWebSocket } from '@/context/WebSocketContext';
import { useEffect, useRef } from 'react';

interface Message {
  type: string;
  sender?: string;
  response?: string;
  thought?: string;
  content?: string;
}

const roleThemes = {
  Host: {
    border: 'border-yellow-500',
    bg: 'bg-yellow-500/10',
    text: 'text-yellow-400',
    highlight: 'bg-[#2a2a4e]'
  },
  System: {
    border: 'border-purple-500',
    bg: 'bg-purple-500/10',
    text: 'text-purple-400',
    highlight: ''
  },
  default: {
    border: 'border-blue-500',
    bg: 'bg-blue-500/10',
    text: 'text-blue-400',
    highlight: ''
  }
};

const MessageBoard = () => {
  const { messages } = useWebSocket();
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
    
    // Log system messages to console
    messages.forEach(message => {
      if (message.type === 'system') {
        console.log('System Message:', message.content);
      }
    });
  }, [messages]);

  const getTheme = (sender?: string) => {
    if (sender?.startsWith('Host')) return roleThemes.Host;
    if (sender === 'System') return roleThemes.System;
    return roleThemes.default;
  };

  const renderMessage = (message: Message) => {
    // Skip rendering system messages
    if (message.type === 'system') {
      return null;
    }

    const theme = getTheme(message.sender);

    return (
      <div className={`mb-3 bg-[#16213e] rounded-lg p-3 border-l-4 ${theme.border} ${theme.highlight}`}>
        <div className="message">
          <span className={`font-bold ${theme.text}`}>{message.sender}:</span>
          <span className="text-gray-200 ml-2">{message.response}</span>
        </div>
        {message.thought && (
          <div className={`thought mt-2 p-2 ${theme.bg} rounded-md border border-green-500/30 text-gray-400 text-sm`}>
            💭 {message.thought}
          </div>
        )}
      </div>
    );
  };

  return (
    <Card className="!bg-[#1a1a2e] !border-[#3a4f7a] !h-[480px] relative">
      <div className="absolute top-0 left-0 right-0 bg-[#16213e] p-3 border-b-2 border-[#3a4f7a] flex items-center justify-between">
        <div className="text-lg font-bold text-white">Game Messages</div>
        <div className="flex gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
        </div>
      </div>

      <div 
        ref={logRef}
        className="h-[calc(480px-48px)] mt-12 overflow-y-auto px-4 font-mono text-sm custom-scrollbar"
      >
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-500 bg-[#16213e] px-4 py-2 rounded-lg border border-[#3a4f7a]">
              Waiting for game messages...
            </div>
          </div>
        ) : (
          <div className="py-4 space-y-1">
            {messages.map((msg, index) => (
              <div key={index}>
                {renderMessage(msg)}
              </div>
            ))}
          </div>
        )}
      </div>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #16213e;
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #3a4f7a;
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #4a5f8a;
        }
        .font-pixel {
          font-family: 'Press Start 2P', monospace;
          font-size: 0.9em;
          line-height: 1.5;
        }
      `}</style>
    </Card>
  );
};

export default MessageBoard; 