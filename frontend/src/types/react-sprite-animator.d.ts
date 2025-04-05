declare module 'react-sprite-animator' {
  interface SpriteAnimatorProps {
    sprite: string;
    width: number;
    height: number;
    fps?: number;
    scale?: number;
    frameCount: number;
    direction?: 'horizontal' | 'vertical';
    shouldAnimate?: boolean;
    startFrame?: number;
    stopLastFrame?: boolean;
    reset?: boolean;
    onEnd?: () => void;
  }

  export default function SpriteAnimator(props: SpriteAnimatorProps): JSX.Element;
} 