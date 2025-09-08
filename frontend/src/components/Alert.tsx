import React, { useEffect } from 'react';
import { CheckCircle, AlertTriangle, X } from 'lucide-react';



interface AlertProps {
  type: 'success' | 'error';
  title: string;
  message: string;
  onClose: () => void;
}   


const Alert: React.FC<AlertProps> = ({ type, title, message, onClose }) => {
  // Automatically close the alert after 5 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000);

    return () => {
      clearTimeout(timer);
    };
  }, [onClose]);

  if (!message) return null;

  const isSuccess = type === 'success';

  const config = {
    containerClasses: isSuccess 
      ? 'bg-green-50 border-green-500 text-green-800' 
      : 'bg-red-50 border-red-500 text-red-800',
    iconColor: isSuccess 
      ? 'text-green-500' 
      : 'text-red-500',
    closeIconColor: isSuccess 
      ? 'text-green-600 hover:text-green-800' 
      : 'text-red-600 hover:text-red-800',
    IconComponent: isSuccess ? CheckCircle : AlertTriangle,
  };

  return (
    // This container creates the popup effect in the bottom-right corner
    <div className="fixed bottom-5 right-5 z-50 w-full max-w-sm animate-slide-up">
        <div className={`w-full border-l-4 p-4 rounded-md shadow-lg ${config.containerClasses}`} role="alert">
            <div className="flex">
                <div className="py-1">
                    <config.IconComponent className={`h-6 w-6 mr-4 ${config.iconColor}`} />
                </div>
                <div>
                    <p className="font-bold">{title}</p>
                    <p className="text-sm">{message}</p>
                </div>
                <button onClick={onClose} className="ml-auto pl-3">
                    <X className={`h-5 w-5 ${config.closeIconColor}`} />
                </button>
            </div>
        </div>
    </div>
  );
};

export default Alert;