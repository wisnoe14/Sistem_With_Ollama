import React from "react";

interface LoadingSpinnerProps {
  /**
   * Optional text to display next to the spinner.
   */
  text?: string;
  /**
   * Defines the size of the spinner dots. Defaults to "md".
   */
  size?: "sm" | "md" | "lg";
  /**
   * Tailwind CSS class for the text color. Defaults to "text-gray-700".
   */
  textColor?: string;
  /**
   * Tailwind CSS class for the spinner dot color. Defaults to "bg-blue-500".
   */
  spinnerColor?: string;
}

/**
 * A modern, attractive loading spinner component featuring three pulsing dots.
 * It's designed to center itself within its parent container.
 */
const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  text,
  size = "md",
  textColor = "text-gray-700",
  spinnerColor = "bg-blue-500",
}) => {
  // Maps the size prop to corresponding Tailwind CSS classes for the dots.
  const sizeClasses = {
    sm: "w-2 h-2",
    md: "w-2.5 h-2.5",
    lg: "w-3 h-3",
  };

  return (
    <div className="w-full h-full flex items-center justify-center gap-3" aria-live="polite" role="status">
      {/* Container for the three animated dots */}
      <div className="flex items-center justify-center space-x-1.5">
        <div
          className={`${sizeClasses[size]} ${spinnerColor} rounded-full animate-pulse`}
          // Inline style is used for animation-delay as Tailwind doesn't have dedicated classes for it.
          // This creates a sequential pulsing effect.
          style={{ animationDelay: '-0.3s' }}
        ></div>
        <div
          className={`${sizeClasses[size]} ${spinnerColor} rounded-full animate-pulse`}
          style={{ animationDelay: '-0.15s' }}
        ></div>
        <div
          className={`${sizeClasses[size]} ${spinnerColor} rounded-full animate-pulse`}
        ></div>
      </div>
      
      {/* Display the text if it's provided */}
      {text && <span className={`text-sm font-medium ${textColor}`}>{text}</span>}
    </div>
  );
};

export default LoadingSpinner;
