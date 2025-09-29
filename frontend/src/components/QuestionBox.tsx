import React, { useState } from "react";

interface QuestionBoxProps {
  question: string;
  options?: string[];
  loading: boolean;
  isClosing: boolean;
  onAnswer: (answer: string, closing: boolean) => void;
}

export default function QuestionBox({
  question,
  options = [],
  loading,
  isClosing,
  onAnswer,
}: QuestionBoxProps) {
  const [manualAnswer, setManualAnswer] = useState("");

  // Batasi maksimal 4 opsi, fallback ke ['Selesai'] jika isClosing dan options kosong
  let limitedOptions: string[] = [];
  if (isClosing) {
    limitedOptions = ["Selesai"];
  } else if (Array.isArray(options) && options.length > 0) {
    limitedOptions = options.slice(0, 4);
  }

  const handleManualSubmit = () => {
    if (manualAnswer.trim()) {
      onAnswer(manualAnswer, isClosing);
      setManualAnswer("");
    }
  };

  return (
    <div className="w-full bg-white/80 backdrop-blur-lg p-6 rounded-2xl shadow-xl border border-gray-200 space-y-5">
      {/* Pertanyaan */}
      <div>
        <p className="text-sm font-semibold text-blue-700 mb-2">
          Pertanyaan AI:
        </p>
        <p
          className="text-xl font-semibold text-gray-800"
          style={{
            fontFamily: "Times New Roman, Times, serif",
            whiteSpace: "pre-line",
            lineHeight: "1.6",
            marginBottom: "12px",
            textAlign: "justify",
            background: "#f8f8f8",
            borderRadius: "8px",
            padding: "16px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
          }}
        >
          {question}
        </p>
      </div>

      {/* Opsi Jawaban */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {limitedOptions.map((opt, i) => (
          <button
            key={i}
            onClick={() => onAnswer(opt, isClosing)}
            disabled={loading}
            className={
              isClosing
                ? "w-full p-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all duration-200 disabled:bg-gray-400 text-center"
                : "text-left p-4 bg-white hover:bg-blue-50 border border-gray-300 rounded-lg transition-all duration-200 disabled:opacity-50 hover:border-blue-400 hover:shadow-md font-medium text-gray-700"
            }
          >
            {isClosing ? "Selesai" : opt}
          </button>
        ))}
      </div>

      {/* Separator ATAU */}
      <div className="relative flex items-center">
        <hr className="w-full border-gray-300" />
        <span className="absolute left-1/2 -translate-x-1/2 bg-white/80 px-2 text-sm text-gray-500 font-medium">
          ATAU
        </span>
      </div>

      {/* Jawaban Manual */}
      <div className="space-y-3">
        <textarea
          className="w-full p-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none transition-shadow"
          rows={3}
          placeholder="Ketik jawaban manual di sini..."
          value={manualAnswer}
          onChange={(e) => setManualAnswer(e.target.value)}
          disabled={loading}
        />
        <button
          onClick={handleManualSubmit}
          disabled={loading || !manualAnswer.trim()}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all disabled:bg-gray-400"
        >
          {loading ? "Memproses..." : isClosing ? "Selesai" : "Lanjutkan"}
        </button>
      </div>
    </div>
  );
}
