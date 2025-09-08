import React from 'react';
import { Send, MessageSquare, CornerDownLeft, Zap } from 'lucide-react';
import AnimatedCard from './AnimatedCard';

// A more modern, visually appealing loading spinner with pulsing dots.
const LoadingSpinner = () => (
  <div className="flex items-center justify-center gap-2">
    <span className="text-sm font-medium text-slate-300">Memproses</span>
    <div className="flex items-center justify-center space-x-1.5">
      <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-slate-300" style={{ animationDelay: '-0.3s' }} />
      <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-slate-300" style={{ animationDelay: '-0.15s' }} />
      <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-slate-300" />
    </div>
  </div>
);

// Re-using the AnimatedCard component assumption from your original code.
// If it's not available, you can replace <AnimatedCard> with a <div>.

interface AnswerInputProps {
  question: string;
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
  options?: string[]; // Opsi jawaban cepat
  onOptionSelect?: (option: string) => void; // Fungsi saat opsi dipilih
}

/**
 * An enhanced, modern input component for answering questions in a chat-like interface.
 * Features a refined dark theme, quick reply options, and manual text input.
 */
const AnswerInput: React.FC<AnswerInputProps> = ({
  question,
  value,
  onChange,
  onSubmit,
  loading,
  options,
  onOptionSelect
}) => {

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Ctrl+Enter or Cmd+Enter, ensuring the input is not empty and not loading.
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey) && !loading && value?.trim()) {
      e.preventDefault(); // Prevents new line on submission
      onSubmit();
    }
  };

  return (
    <AnimatedCard className="w-full rounded-2xl bg-white p-8 shadow-lg border border-gray-200 min-h-[50vh] flex flex-col items-center justify-center text-center">
      {/* Header Section */}
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600">
          <MessageSquare className="h-5 w-5 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-slate-900">
            Pertanyaan AI:
          </h3>
        </div>
      </div>

      {/* Question Display Section */}
      <div className="my-5 rounded-lg bg-white p-4 border border-gray-200">
        <p className="text-base font-medium leading-relaxed text-gray-800">
          {question}
        </p>
      </div>

      {/* Quick Reply Options Section */}
      {options && options.length > 0 && (
        <div className="mb-5">
          <div className="flex items-center gap-2 text-sm text-slate-500 mb-3">
            <Zap className="h-4 w-4 text-yellow-400" />
            <span>Opsi Jawaban Cepat</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {options.map((option, index) => (
              <button
                key={index}
                onClick={() => onOptionSelect?.(option)}
                disabled={loading}
                className="px-4 py-2 rounded-full bg-slate-100 text-gray-800 text-sm font-medium
                           hover:bg-blue-50 transition-colors duration-200
                           disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {option}
              </button>
            ))}
          </div>
          <hr className="border-gray-200 my-4" />
        </div>
      )}

      {/* Divider ATAU */}
      <div className="flex items-center w-full my-4">
        <div className="flex-grow border-t border-gray-200"></div>
        <span className="mx-4 text-gray-400 font-semibold">ATAU</span>
        <div className="flex-grow border-t border-gray-200"></div>
      </div>

      {/* Textarea and Submission Section */}
      <div className="space-y-4 w-full max-w-lg">
        <div className="relative">
          <textarea
            className="w-full min-h-[100px] resize-none rounded-lg border border-gray-300 bg-white px-4 py-3 
                       text-gray-800 placeholder:text-gray-400 transition-colors duration-300 
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={loading}
            placeholder="Ketik jawaban manual di sini..."
            onKeyDown={handleKeyDown}
            autoFocus
          />
          {/* Keyboard shortcut hint */}
          <div className="absolute bottom-2 right-3 flex items-center gap-1 text-xs text-gray-400">
            <span className="font-mono text-xs">Ctrl</span>
            <CornerDownLeft className="h-3 w-3" />
          </div>
        </div>

        <button
          className={`
            w-full py-3 px-4 rounded-lg font-semibold text-base
            flex items-center justify-center gap-2
            transition-all duration-300 transform active:scale-[0.98]
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white focus:ring-blue-500
            ${loading || !value?.trim()
              ? 'bg-gray-300 text-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20'
            }
          `}
          onClick={onSubmit}
          disabled={loading || !value?.trim()}
        >
          {loading ? (
            <LoadingSpinner />
          ) : (
            <>
              <Send className="h-5 w-5" />
              Kirim Jawaban Manual
            </>
          )}
        </button>
      </div>
    </AnimatedCard>
  );
};

export default AnswerInput;
