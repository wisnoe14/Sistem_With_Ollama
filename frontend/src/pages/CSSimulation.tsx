import { useState, useEffect, useRef } from 'react';
import { 
    Bot, 
    Settings, 
    Sparkles, 
    ChevronDown, 
    CreditCard, 
    ShieldCheck, 
    Target, 
    Loader2, 
    CheckCircle2, 
    XCircle, 
    FileDown,
    LogOut
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

// Fungsi untuk memanggil intent OpenAI
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const CSSimulation = () => {
    // One-shot generation states
    // Step-by-step mode: no local allQuestions/stepIndex
    const [topic, setTopic] = useState<Topic>("telecollection");
    const [currentQuestion, setCurrentQuestion] = useState<ScenarioItem | null>(null);
    const [conversation, setConversation] = useState<ConversationItem[]>([]);
    const [result, setResult] = useState<Prediction | null>(null);
    const [loading, setLoading] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [simulationHistory, setSimulationHistory] = useState<HistoryItem[]>([]);
    const [isStatusStep, setIsStatusStep] = useState(false);
    const navigate = useNavigate();


    // --- Backend Configuration ---
    // API_BASE_URL is already declared at the top of the file.

    // --- Type Definitions ---
    type Topic = "telecollection" | "retention" | "winback";

    type ScenarioItem = {
        q: string;
        options: string[];
    };

    type ConversationItem = {
        q: string;
        a: string;
    };

    type Prediction = {
    pertanyaan_cs?: string;
    jawaban_pelanggan?: string;
        customer_id?: string;
        mode?: string;
        status_dihubungi?: string;
        status: string;
        jenis_promo?: string;
        estimasi_pembayaran: string;
        alasan: string;
        minat?: string;
        promo?: string;
        intent?: string;
    };

    type HistoryItem = {
        date: string;
        topic: string;
        result: Prediction;
    };

    // --- HELPER COMPONENTS ---

    const LoadingSpinner = ({ text }: { text: string }) => (
        <div className="flex items-center justify-center gap-2 text-white">
            <Loader2 className="animate-spin h-5 w-5" />
            <span>{text}</span>
        </div>
    );

    // --- CUSTOM DROPDOWN COMPONENT ---
    type DropdownOption = {
        key: string;
        label: string;
        icon: React.ComponentType<{ className?: string }>;
    };

    interface CustomDropdownProps {
        options: DropdownOption[];
        selected: string;
        onSelect: (key: string) => void;
        disabled: boolean;
    }

    const CustomDropdown = ({ options, selected, onSelect, disabled }: CustomDropdownProps) => {
        const [isOpen, setIsOpen] = useState(false);
        const dropdownRef = useRef<HTMLDivElement>(null);
        const selectedOption = options.find(opt => opt.key === selected);

        useEffect(() => {
            const handleClickOutside = (event: MouseEvent) => {
                if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                    setIsOpen(false);
                }
            };
            document.addEventListener("mousedown", handleClickOutside);
            return () => document.removeEventListener("mousedown", handleClickOutside);
        }, []);

        return (
            <div className="relative" ref={dropdownRef}>
                <button
                    type="button"
                    onClick={() => setIsOpen(!isOpen)}
                    disabled={disabled}
                    className="w-full flex items-center justify-between appearance-none bg-gray-50 border border-gray-300 rounded-lg px-4 py-3 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:bg-gray-200 disabled:cursor-not-allowed"
                >
                    <span className="font-semibold text-gray-700">{selectedOption?.label || 'Pilih Opsi'}</span>
                    <ChevronDown className={`w-5 h-5 text-gray-500 transition-transform duration-300 ${isOpen ? 'transform rotate-180' : ''}`} />
                </button>

                {isOpen && !disabled && (
                    <div className="absolute z-10 w-full mt-2 bg-white rounded-lg shadow-2xl border border-gray-100 overflow-hidden animate-fade-in-down">
                        <ul className="py-1">
                            {options.map((option) => (
                                <li
                                    key={option.key}
                                    onClick={() => {
                                        onSelect(option.key);
                                        setIsOpen(false);
                                    }}
                                    className="px-4 py-3 text-gray-800 hover:bg-blue-50 cursor-pointer flex items-center gap-3 transition-colors duration-150"
                                >
                                    <option.icon className="w-5 h-5 text-blue-600" />
                                    <span className="font-medium">{option.label}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        );
    };


    // --- MAIN COMPONENTS ---
    const ScenarioControls = ({ topic, setTopic, isGenerating, disabled, isSimulationRunning, onStart, onEnd }: {
        topic: Topic;
        setTopic: (topic: Topic) => void;
        isGenerating: boolean;
        disabled: boolean;
        isSimulationRunning: boolean;
        onStart: () => void;
        onEnd: () => void;
    }) => {
        const TOPICS = [
            { key: "telecollection", label: "Telecollection", description: "Penagihan & Recovery", icon: CreditCard },
            { key: "retention", label: "Retention", description: "Pencegahan Churn", icon: ShieldCheck },
            { key: "winback", label: "Winback", description: "Reaktivasi Customer", icon: Target },
        ];
        const selectedTopic = TOPICS.find(t => t.key === topic);
        const SelectedIcon = selectedTopic?.icon ?? CreditCard;

        // Guard: lock request selama isGenerating
        const [locked, setLocked] = useState(false);
        useEffect(() => {
            if (isGenerating) setLocked(true);
            else setLocked(false);
        }, [isGenerating]);
        return (
            <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-200 space-y-6">
                <div className="flex items-center gap-3">
                    <Settings className="w-6 h-6 text-blue-600" />
                    <h3 className="text-lg font-bold text-gray-800">Pengaturan Skenario</h3>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-600 mb-2">Pilih Topik Simulasi</label>
                    <CustomDropdown
                        options={TOPICS}
                        selected={topic}
                        onSelect={(key) => setTopic(key as Topic)}
                        disabled={disabled || locked}
                    />
                </div>
                <div className="p-4 rounded-xl bg-blue-50 border border-blue-200">
                    <div className="flex items-center gap-4">
                        <div className="bg-white p-2 rounded-full shadow-sm">
                            <SelectedIcon className="w-7 h-7 text-blue-600" />
                        </div>
                        <div>
                            <h4 className="font-bold text-gray-800">{selectedTopic ? selectedTopic.label : ''}</h4>
                            <p className="text-sm text-gray-600">{selectedTopic ? selectedTopic.description : ''}</p>
                        </div>
                    </div>
                </div>
                <button
                    className={`w-full px-6 py-4 rounded-xl font-bold text-white flex items-center justify-center gap-3 text-lg transition-all duration-300 transform active:scale-95 shadow-lg ${isSimulationRunning ? 'bg-red-600 hover:bg-red-700' : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'}`}
                    onClick={() => {
                        if (!locked) {
                            if (isSimulationRunning) onEnd();
                            else onStart();
                        }
                    }}
                    disabled={isGenerating || locked}
                >
                    {isGenerating ? <LoadingSpinner text={isSimulationRunning ? 'Mengakhiri...' : 'Starting...'} /> : (
                  <>
                    {isSimulationRunning ? <LogOut className="w-6 h-6" /> : <Sparkles className="w-6 h-6" />}
                    {isSimulationRunning ? 'End Simulasi' : 'Mulai Simulasi'}
                  </>
                )}
                </button>
            </div>
        );
    };

    const AnswerInput = ({ question, options, onAnswer, loading }: {
        question: string;
        options: string[];
        onAnswer: (answer: string) => void;
        loading: boolean;
    }) => {
        const [manualAnswer, setManualAnswer] = useState("");

        const submitManual = () => {
            if (manualAnswer.trim()) {
                onAnswer(manualAnswer);
                setManualAnswer("");
            }
        };

        // Batasi opsi maksimal 4 dan fallback jika kosong
        const limitedOptions = Array.isArray(options) && options.length > 0 ? options.slice(0, 4) : ['Jawab manual'];
        return (
            <div className="w-full max-w-2xl mx-auto bg-white/80 backdrop-blur-lg p-6 rounded-2xl shadow-xl border border-gray-200 space-y-5">
                <div>
                    <p className="text-sm font-semibold text-blue-700 mb-2">Pertanyaan AI:</p>
                    <p
                        className="text-xl font-semibold text-gray-800"
                        style={{
                            fontFamily: 'Times New Roman, Times, serif',
                            whiteSpace: 'pre-line',
                            lineHeight: '1.6',
                            marginBottom: '12px',
                            textAlign: 'justify',
                            background: '#f8f8f8',
                            borderRadius: '8px',
                            padding: '16px',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
                        }}
                    >
                        {question}
                    </p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {limitedOptions.map((opt, i) => (
                        <button key={i} onClick={() => onAnswer(opt)} disabled={loading} className="text-left p-4 bg-white hover:bg-blue-50 border border-gray-300 rounded-lg transition-all duration-200 disabled:opacity-50 hover:border-blue-400 hover:shadow-md font-medium text-gray-700">
                            {opt}
                        </button>
                    ))}
                </div>
                <div className="relative flex items-center">
                    <hr className="w-full border-gray-300" />
                    <span className="absolute left-1/2 -translate-x-1/2 bg-white/80 px-2 text-sm text-gray-500 font-medium">ATAU</span>
                </div>
                <div className="space-y-3">
                    <textarea
                        className="w-full p-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none transition-shadow"
                        rows={3}
                        placeholder="Ketik jawaban manual di sini..."
                        value={manualAnswer}
                        onChange={(e) => setManualAnswer(e.target.value)}
                        disabled={loading}
                    />
                    <button onClick={submitManual} disabled={loading || !manualAnswer.trim()} className="w-full py-3 bg-gray-700 hover:bg-gray-800 text-white font-semibold rounded-lg transition-all disabled:bg-gray-400">
                        {loading ? 'Memproses...' : 'Kirim Jawaban Manual'}
                    </button>
                </div>
            </div>
        );
    };

    const PredictionResult = ({ result, topic, onReset }: {
        result: Prediction;
        topic: string;
        onReset: () => void;
    }) => {
        const isSuccess = result.status === 'Success';
        return (
            <div className="w-full max-w-2xl mx-auto bg-white p-8 rounded-2xl shadow-2xl border border-gray-200 space-y-6">
                <div className="text-center">
                    <div className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center ${isSuccess ? 'bg-green-100' : 'bg-red-100'}`}> 
                        {isSuccess ? <CheckCircle2 className="w-10 h-10 text-green-600" /> : <XCircle className="w-10 h-10 text-red-600" />}
                    </div>
                    <h2 className="text-3xl font-bold text-gray-800 mt-4">Hasil Prediksi AI</h2>
                    <p className="text-gray-500">Analisis untuk skenario: <span className="font-semibold">{topic}</span></p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="bg-gray-50 p-4 rounded-lg"><strong>Customer ID:</strong> <span className="font-semibold text-gray-800">{result.customer_id}</span></div>
                    <div className="bg-gray-50 p-4 rounded-lg"><strong>Mode:</strong> <span className="font-semibold text-gray-800">{result.mode}</span></div>
                    <div className="bg-gray-50 p-4 rounded-lg"><strong>Status Dihubungi:</strong> <span className="font-semibold text-gray-800">{result.status_dihubungi}</span></div>
                    <div className="bg-gray-50 p-4 rounded-lg"><strong>Status:</strong> <span className={`font-semibold ${isSuccess ? 'text-green-700' : 'text-red-700'}`}>{result.status}</span></div>
                    <div className="bg-gray-50 p-4 rounded-lg"><strong>Jenis Promo:</strong> <span className="font-semibold text-gray-800">{result.jenis_promo}</span></div>
                    <div className="bg-gray-50 p-4 rounded-lg"><strong>Estimasi Pembayaran:</strong> <span className="font-semibold text-gray-800">{result.estimasi_pembayaran}</span></div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <h4 className="font-semibold text-gray-800 mb-1">Ringkasan Alasan:</h4>
                    <p className="text-gray-700">{result.alasan}</p>
                </div>
                <button onClick={onReset} className="w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg transition-all shadow-lg">End Simulasi</button>
            </div>
        );
    };
    
            
    const SimulationHistory = ({ history, onExport }: {
        history: HistoryItem[];
        onExport: () => void;
    }) => {
        if (history.length === 0) return null;
        return (
            <div className="mt-12 bg-white p-6 rounded-2xl shadow-lg border border-gray-200">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-4">
                    <h3 className="text-xl font-bold text-gray-800">Riwayat Simulasi</h3>
                    <button onClick={onExport} className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg text-sm transition-colors shadow-md">
                        <FileDown className="w-4 h-4" />
                        Ekspor ke Excel
                    </button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-gray-600">
                        <thead className="text-xs text-gray-700 uppercase bg-gray-100">
                            <tr>
                                <th className="px-6 py-3">Customer ID</th>
                                <th className="px-6 py-3">Mode</th>
                                <th className="px-6 py-3">Status Dihubungi</th>
                                <th className="px-6 py-3">Pertanyaan CS</th>
                                <th className="px-6 py-3">Jawaban Pelanggan</th>
                                <th className="px-6 py-3">Status</th>
                                <th className="px-6 py-3">Jenis Promo</th>
                                <th className="px-6 py-3">Estimasi Pembayaran</th>
                                <th className="px-6 py-3">Alasan</th>
                            </tr>
                        </thead>
                        <tbody>
                            {history.map((item, index) => (
                                <tr key={index} className="bg-white border-b hover:bg-gray-50">
                                    <td className="px-6 py-4">{item.result.customer_id || '-'}</td>
                                    <td className="px-6 py-4">{item.result.mode || '-'}</td>
                                    <td className="px-6 py-4">{item.result.status_dihubungi || '-'}</td>
                                    <td className="px-6 py-4">{item.result.pertanyaan_cs || '-'}</td>
                                    <td className="px-6 py-4">{item.result.jawaban_pelanggan || '-'}</td>
                                    <td className="px-6 py-4">{item.result.status || '-'}</td>
                                    <td className="px-6 py-4">{item.result.jenis_promo || '-'}</td>
                                    <td className="px-6 py-4">{item.result.estimasi_pembayaran || '-'}</td>
                                    <td className="px-6 py-4">{item.result.alasan || '-'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        );
    };

    // --- APP COMPONENT ---

    const handleStart = async () => {
        setIsGenerating(true);
        setResult(null);
        setConversation([]);
        setIsStatusStep(true);
        try {
            const response = await fetch(`${API_BASE_URL}/conversation/status-dihubungi-options`);
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            // setStatusDihubungiOptions(Array.isArray(data.options) ? data.options : []);
            // No need to set statusDihubungiOptions, just use data.options directly.
            setCurrentQuestion({ q: data.question, options: Array.isArray(data.options) ? data.options : [] });
        } catch (error) {
            console.error("Failed to fetch status dihubungi options:", error);
            alert("Gagal mengambil opsi status dihubungi dari server. Silakan coba lagi.");
            setCurrentQuestion(null);
        } finally {
            setIsGenerating(false);
        }
    };


    const handleAnswer = async (answer: string) => {
        setLoading(true);
        let newConversation;
        let status = "";
        const customer_id = sessionStorage.getItem('customer_id') || "";
        const token = sessionStorage.getItem('token');

        if (isStatusStep) {
        setIsStatusStep(false);
        let statusQ = answer.trim();
        if (statusQ === "Bisa Dihubungi" || statusQ === "Tidak Dapat Dihubungi") {
            // OK
        } else {
            if (statusQ.toLowerCase().includes("bisa")) statusQ = "Bisa Dihubungi";
            else if (statusQ.toLowerCase().includes("tidak")) statusQ = "Tidak Dapat Dihubungi";
        }
        newConversation = [...conversation, { q: currentQuestion?.q || "Status dihubungi?", a: statusQ }];
        setConversation(newConversation);
        status = statusQ;

        try {
            // Simpan percakapan ke backend
            const saveRes = await fetch(`${API_BASE_URL}/conversation/next-question`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                },
                body: JSON.stringify({ customer_id, topic, conversation: newConversation }),
            });
            if (!saveRes.ok) throw new Error('Gagal menyimpan percakapan');
            const saveData = await saveRes.json();
            if (!saveData.success) throw new Error(saveData.error || 'Gagal menyimpan percakapan');

            // Generate pertanyaan berikutnya (bisa alasan, prediksi, atau pertanyaan lain)
            const response = await fetch(`${API_BASE_URL}/conversation/generate-simulation-questions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                },
                body: JSON.stringify({ customer_id, topic, conversation: newConversation, status }),
            });
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            if (data.is_last) {
                // Prediction hanya jika is_last
                const prediction = data.prediction;
                setResult(prediction);
                const historyItem: HistoryItem = {
                    date: new Date().toLocaleString('id-ID'),
                    topic: topic,
                    result: prediction
                };
                setSimulationHistory(prev => [historyItem, ...prev]);
                setCurrentQuestion(null);
            } else if (data.question) {
                setCurrentQuestion({ q: data.question, options: data.options || [] });
            } else {
                setCurrentQuestion(null);
            }
        } catch (error) {
            console.error("Gagal menyimpan percakapan atau mendapatkan pertanyaan berikutnya:", error);
            alert("Gagal menyimpan percakapan atau mendapatkan pertanyaan berikutnya dari server.");
        } finally {
            setLoading(false);
        }
        return;
        } else {
            // Jawaban untuk pertanyaan selain status
            if (
                currentQuestion?.q &&
                currentQuestion.q !== "Status dihubungi?" &&
                !(conversation.length > 0 && conversation[conversation.length-1].q === currentQuestion.q && conversation[conversation.length-1].a === answer)
            ) {
                newConversation = [...conversation, { q: currentQuestion.q, a: answer }];
                setConversation(newConversation);
            } else {
                newConversation = [...conversation];
            }
            status = newConversation.find(c => c.q && c.q.toLowerCase().includes('status dihubungi'))?.a || "";

            try {
                // 1. Simpan percakapan ke backend (hanya simpan, tidak prediksi)
                const saveRes = await fetch(`${API_BASE_URL}/conversation/next-question`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(token ? { Authorization: `Bearer ${token}` } : {})
                    },
                    body: JSON.stringify({ customer_id, topic, conversation: newConversation }),
                });
                if (!saveRes.ok) throw new Error('Gagal menyimpan percakapan');
                const saveData = await saveRes.json();
                if (!saveData.success) throw new Error(saveData.error || 'Gagal menyimpan percakapan');

                // 2. Generate pertanyaan berikutnya
                const response = await fetch(`${API_BASE_URL}/conversation/generate-simulation-questions`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(token ? { Authorization: `Bearer ${token}` } : {})
                    },
                    body: JSON.stringify({ customer_id, topic, conversation: newConversation, status }),
                });
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                if (data.is_last) {
                    // Prediction hanya jika is_last
                    // Kirim permintaan prediksi lengkap agar field tidak kosong
                    const predictRes = await fetch(`${API_BASE_URL}/conversation/predict`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            ...(token ? { Authorization: `Bearer ${token}` } : {})
                        },
                        body: JSON.stringify({
                            customer_id,
                            topic,
                            conversation: newConversation,
                        }),
                    });
                    let prediction = data.prediction;
                    if (predictRes.ok) {
                        const predictData = await predictRes.json();
                        if (predictData && predictData.result) {
                            prediction = predictData.result;
                        }
                    }
                    setResult(prediction);
                    const historyItem: HistoryItem = {
                        date: new Date().toLocaleString('id-ID'),
                        topic: topic,
                        result: prediction
                    };
                    setSimulationHistory(prev => [historyItem, ...prev]);
                    setCurrentQuestion(null);
                } else if (data.question) {
                    setCurrentQuestion({ q: data.question, options: data.options || [] });
                } else {
                    setCurrentQuestion(null);
                }
            } catch (error) {
                console.error("Gagal menyimpan percakapan atau mendapatkan pertanyaan berikutnya:", error);
                alert("Gagal menyimpan percakapan atau mendapatkan pertanyaan berikutnya dari server.");
            } finally {
                setLoading(false);
            }
        }
    };

    const handleReset = () => {
    setCurrentQuestion(null);
    setResult(null);
    navigate('/Home');
    };

    const handleExport = () => {
        const XLSX = (window as typeof window & { XLSX: typeof import("xlsx") }).XLSX;
        if (!XLSX) {
            alert("Pustaka ekspor Excel tidak ditemukan.");
            return;
        }

        const worksheetData = simulationHistory.map(item => ({
            Tanggal: item.date,
            Skenario: item.topic,
            Status: item.result.status,
            Minat: item.result.minat,
            'Estimasi Bayar': item.result.estimasi_pembayaran,
            Promo: item.result.promo,
            Alasan: item.result.alasan
        }));
        const worksheet = XLSX.utils.json_to_sheet(worksheetData);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, "Riwayat Simulasi");
        XLSX.writeFile(workbook, "Riwayat_Simulasi_CS.xlsx");
    };

    

    const isSimulationRunning = currentQuestion !== null && !result;

    // Ambil nama dari sessionStorage
    const customerName = sessionStorage.getItem('customer_name') || '';
    const getInitials = (name: string) => {
      if (!name) return '';
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0,2);
    };

    return (
        <div className="min-h-screen bg-gray-100 font-sans">
             <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
                body { font-family: 'Inter', sans-serif; }
                @keyframes fade-in-down {
                    0% { opacity: 0; transform: translateY(-10px); }
                    100% { opacity: 1; transform: translateY(0); }
                }
                .animate-fade-in-down { animation: fade-in-down 0.3s ease-out forwards; }
            `}</style>
            <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-200">
                <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-20">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                                <Bot className="w-7 h-7 text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl sm:text-2xl font-bold text-gray-800">
                                    ICONNET AI Assistant
                                </h1>
                                <p className="text-sm text-gray-500">
                                    Simulasi Customer Service Intelligence
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            {customerName && (
                              <div className="flex items-center gap-3 bg-white border border-gray-200 rounded-xl px-4 py-2 shadow-sm">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
                                  {getInitials(customerName)}
                                </div>
                                <span className="font-semibold text-gray-800 text-base">{customerName}</span>
                              </div>
                            )}
                        </div>
                    </div>
                </div>
            </header>
            <main className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
                    <aside className="lg:col-span-4 xl:col-span-3">
                        <div className="lg:sticky lg:top-28">
                            <ScenarioControls 
                                topic={topic}
                                setTopic={setTopic}
                                isGenerating={isGenerating}
                                disabled={isSimulationRunning || isGenerating}
                                isSimulationRunning={isSimulationRunning}
                                onStart={handleStart}
                                onEnd={handleReset}
                            />
                        </div>
                    </aside>
                    <div className="lg:col-span-8 xl:col-span-9">
                        {!isSimulationRunning && !result && !isGenerating && (
                            <div className="flex flex-col items-center justify-center text-center p-8 bg-white rounded-2xl shadow-lg border border-gray-200 min-h-[50vh]">
                                <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mb-4 ring-4 ring-white/50">
                                    <Bot className="w-10 h-10 text-blue-600" />
                                </div>
                                <h2 className="text-2xl font-bold text-gray-800">Selamat Datang di AI Assistant</h2>
                                <p className="text-gray-500 mt-2 max-w-md">Pilih skenario dan klik "Mulai Simulasi" untuk memulai.</p>
                            </div>
                        )}
                        {isGenerating && (
                            <div className="flex flex-col items-center justify-center text-center p-8 bg-white rounded-2xl shadow-lg border border-gray-200 min-h-[50vh]">
                                <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
                                <p className="text-gray-600 mt-4">Mempersiapkan skenario AI, mohon tunggu...</p>
                            </div>
                        )}
                        {isSimulationRunning && currentQuestion && (
                            <AnswerInput 
                                question={currentQuestion.q}
                                options={currentQuestion.options}
                                onAnswer={handleAnswer}
                                loading={loading}
                            />
                        )}
                        {result && (
                            <PredictionResult result={result} topic={topic} onReset={handleReset} />
                        )}
                        <SimulationHistory history={simulationHistory} onExport={handleExport} />
                    </div>
                </div>
            </main>
        </div>
    );
};

export default CSSimulation;
