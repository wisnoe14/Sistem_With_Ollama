import React from "react";
import { cn } from "../lib/utils";

interface AnimatedCardProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

const AnimatedCard: React.FC<AnimatedCardProps> = ({ 
  children, 
  className,
  delay = 0 
}) => {
  return (
    <div 
      className={cn(
        "opacity-0 translate-y-4 animate-fade-in animate-fadeIn",
        className
      )}
      style={{
        animationDelay: `${delay}ms`,
        animationFillMode: 'forwards'
      }}
    >
      {children}
    </div>
  );
};

export default AnimatedCard;