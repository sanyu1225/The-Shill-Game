"use client";

import Image from 'next/image';
import { useEffect, useState } from 'react';

interface CharacterProps {
  spriteIndex: number;
  isEntering?: boolean;
}

const Character = ({ spriteIndex, isEntering = true }: CharacterProps) => {
  // 精灵图的尺寸配置
  const SPRITE_WIDTH = 32;    // 每个精灵的宽度
  const SPRITE_HEIGHT = 32;   // 每个精灵的高度（修正为32px）
  const SCALE = 2;           // 放大倍数
  const FRAME_COUNT = 2;     // 每行2帧
  const ANIMATION_SPEED = 300; // 动画速度（毫秒）

  const [currentFrame, setCurrentFrame] = useState(0);
  const [isWalking, setIsWalking] = useState(isEntering);

  // 走路动画
  useEffect(() => {
    if (!isWalking) return;

    const interval = setInterval(() => {
      setCurrentFrame(prev => (prev + 1) % FRAME_COUNT);
    }, ANIMATION_SPEED);

    return () => clearInterval(interval);
  }, [isWalking]);

  // 监听入场状态
  useEffect(() => {
    setIsWalking(isEntering);
    
    // 入场动画结束后停止走路
    if (isEntering) {
      const timer = setTimeout(() => {
        setIsWalking(false);
        setCurrentFrame(0);
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [isEntering]);

  // 入场动画
  const entranceAnimation = isEntering ? {
    animation: 'character-entrance 2s forwards',
  } : {};

  // 计算精灵图的位置
  const spritePosition = {
    objectPosition: isWalking 
      ? `-${currentFrame * SPRITE_WIDTH}px -${SPRITE_HEIGHT}px` // 下面一行（朝后走）
      : `-${currentFrame * SPRITE_WIDTH}px 0` // 上面一行（朝前站）
  };

  return (
    <div
      style={{
        width: SPRITE_WIDTH * SCALE,
        height: SPRITE_HEIGHT * SCALE,
        ...entranceAnimation
      }}
    >
      <div 
        className="relative w-full h-full overflow-hidden"
        style={{
          imageRendering: 'pixelated'
        }}
      >
        <Image
          src={`/Characters/${spriteIndex}.png`}
          alt={`Character ${spriteIndex}`}
          width={64}   // 2x2 布局，总宽64px
          height={64}  // 2x2 布局，总高64px
          className="object-none"
          style={{
            ...spritePosition,
            transform: `scale(${SCALE})`,
            transformOrigin: 'top left'
          }}
          priority
        />
      </div>

      <style jsx global>{`
        @keyframes character-entrance {
          0% {
            transform: translate(400px, 200px);
          }
          100% {
            transform: translate(0, 0);
          }
        }
      `}</style>
    </div>
  );
};

export default Character; 