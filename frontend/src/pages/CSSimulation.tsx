import { useState, useEffect, useRef } from 'react';
// import * as XLSX from "xlsx";
import { useNavigate } from 'react-router-dom';
import {
    Bot,
    Settings,
    ChevronDown,
    CreditCard,
    ShieldCheck,
    Target,
} from 'lucide-react';
// Fungsi untuk memanggil intent OpenAI
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1/endpoints";




const CSSimulation = () => {
    // Opsi alasan tidak dapat dihubungi
    const alasanOptions = [
        "Nomor tidak aktif",
        "Tidak diangkat",
        "Salah sambung",
        "Lainnya"
    ];
    // One-shot generation states
    // Step-by-step mode: no local allQuestions/stepIndex
    const [topic, setTopic] = useState<Topic>("telecollection");
    const [currentQuestion, setCurrentQuestion] = useState<ScenarioItem | null>(null);
    const [conversation, setConversation] = useState<ConversationItem[]>([]);
    const [result, setResult] = useState<Prediction | null>(null);
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [, setSimulationHistory] = useState<HistoryItem[]>(() => {
        const saved = localStorage.getItem('simulationHistory');
        const history = saved ? JSON.parse(saved) : [];
        
        // Remove duplicates on load
        const uniqueHistory = history.filter((item: HistoryItem, index: number) => {
            // Keep item if no duplicate found in previous items
            return !history.slice(0, index).some((prevItem: HistoryItem) => 
                prevItem.customer_id === item.customer_id &&
                prevItem.topik === item.topik &&
                prevItem.status === item.status &&
                prevItem.alasan === item.alasan &&
                Math.abs(new Date(prevItem.tanggal).getTime() - new Date(item.tanggal).getTime()) < 5000 // within 5 seconds
            );
        });
        
        if (uniqueHistory.length !== history.length) {
            localStorage.setItem('simulationHistory', JSON.stringify(uniqueHistory));
        }
        
        return uniqueHistory;
    });

    // Helper untuk menambah data ke history dengan format tabel
    function addToSimulationHistory({ status, alasan, estimasi_pembayaran, risk_level, risk_label, risk_color }: { status: string; alasan: string; estimasi_pembayaran?: string; risk_level?: string; risk_label?: string; risk_color?: string }) {
        console.log('[addToSimulationHistory] 📝 Called with:', { status, alasan, estimasi_pembayaran, risk_level, risk_label, risk_color });
        console.log('[addToSimulationHistory] Current topic state:', topic);
        
        // Validasi data sebelum disimpan - hanya tolak jika benar-benar kosong
        if (!status || !alasan || !topic || 
            status.trim() === '' || alasan.trim() === '' || topic.trim() === '' ||
            status === 'undefined' || alasan === 'undefined') {
            console.warn('⚠️ Skipping invalid history data:', { 
                status, alasan, topic,
                statusValid: !!status,
                alasanValid: !!alasan, 
                topicValid: !!topic
            });
            return;
        }
        
        const now = new Date();
        const tanggal = now.toLocaleDateString('id-ID') + ', ' + now.toLocaleTimeString('id-ID');
        const customer_id = sessionStorage.getItem('customer_id') || '-';
        const nama = sessionStorage.getItem('customer_name') || '-';
        const topik = topic;
    const item = { tanggal, customer_id, nama, topik, status, alasan, estimasi_pembayaran: estimasi_pembayaran || '-', risk_level: risk_level || 'low', risk_label: risk_label || 'Aman', risk_color: risk_color || '#16a34a' };
        
        // Debug: Log data yang akan disimpan
        console.log('💾 Saving to history:', item);
        console.log('💾 Current topic:', topic);
        console.log('💾 Status received:', status);
        console.log('💾 Alasan received:', alasan);
        console.log('🎯 Risk Level:', risk_level);
        console.log('🎯 Risk Label:', risk_label);
        console.log('🎯 Risk Color:', risk_color);
        
        setSimulationHistory(prev => {
            // Prevent double entry: check if last entry is duplicate for same customer/topic
            if (prev.length > 0) {
                const lastEntry = prev[0];
                if (lastEntry.customer_id === customer_id && 
                    lastEntry.topik === topik && 
                    lastEntry.status === status &&
                    lastEntry.alasan === alasan) {
                    console.log('🚫 Preventing duplicate history entry');
                    return prev; // Don't add duplicate
                }
            }
            
            const updated = [item, ...prev];
            localStorage.setItem('simulationHistory', JSON.stringify(updated));
            console.log('✅ Successfully saved to localStorage:', updated.length, 'items');
            console.log('✅ Latest saved item:', updated[0]);
            return updated;
        });
    }
    const [statusDihubungi, setStatusDihubungi] = useState<string | null>(null);
    const [showAlasanTidakDihubungi, setShowAlasanTidakDihubungi] = useState(false);
    const [selectedAlasan, setSelectedAlasan] = useState<string | null>(null);
    // const [showCustomerReasonView, setShowCustomerReasonView] = useState(false);
    // const [lastAlasan, setLastAlasan] = useState<string | null>(null);


    // --- Backend Configuration ---
    // API_BASE_URL is already declared at the top of the file.

    // --- Type Definitions ---
    type Topic = "telecollection" | "retention" | "winback";

    type ScenarioItem = {
    q: string;
    options: string[];
    is_closing?: boolean;
    question_followup?: string;
    };

    // Fungsi untuk memanggil prediksi dan navigasi ke halaman hasil
    // Fungsi untuk mengambil prediksi dan simpan ke history
    const fetchPrediction = async () => {
        console.log('[fetchPrediction] 🚀 Starting prediction fetch...');
        console.log('[fetchPrediction] Current topic:', topic);
        console.log('[fetchPrediction] Conversation length:', conversation.length);
        
        setLoading(true);
        try {
            const customer_id = sessionStorage.getItem('customer_id') || "";
            const token = sessionStorage.getItem('token');
            // Pastikan conversation mengandung status dihubungi di awal
            let conversationToSend = [...conversation];
            if (
                statusDihubungi &&
                !conversationToSend.some(item => item.q.toLowerCase().includes('status dihubungi'))
            ) {
                conversationToSend = [
                    { q: 'Status Dihubungi?', a: statusDihubungi || "" },
                    ...conversationToSend
                ];
            }
            // Ambil prediksi dari backend
            const response = await fetch(`${API_BASE_URL}/conversation/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                },
                body: JSON.stringify({
                    customer_id,
                    topic,
                    conversation: conversationToSend
                })
            });
            if (!response.ok) throw new Error('Gagal mengambil prediksi');
            const data = await response.json();
            const prediction = data.result;
            
            // 🔧 DEBUG: Log prediction data untuk troubleshooting
            console.log('[fetchPrediction] Backend response:', data);
            console.log('[fetchPrediction] Prediction data:', prediction);
            console.log('[fetchPrediction] Status:', prediction?.status);
            console.log('[fetchPrediction] Alasan:', prediction?.alasan);
            console.log('[fetchPrediction] Estimasi pembayaran:', prediction?.estimasi_pembayaran);
            console.log('[fetchPrediction] 🎯 Risk Level:', prediction?.risk_level);
            console.log('[fetchPrediction] 🎯 Risk Label:', prediction?.risk_label);
            console.log('[fetchPrediction] 🎯 Risk Color:', prediction?.risk_color);
            
            setResult(prediction);

            // 💾 Simpan ke history SEBELUM navigate
            if (prediction && prediction.status && prediction.alasan) {
                console.log('[fetchPrediction] ✅ Saving to history...');
                addToSimulationHistory({
                    status: prediction.status,
                    alasan: prediction.alasan,
                    estimasi_pembayaran: prediction.estimasi_pembayaran || '-',
                    risk_level: prediction.risk_level,
                    risk_label: prediction.risk_label,
                    risk_color: prediction.risk_color
                });
                console.log('[fetchPrediction] ✅ History saved successfully');
            } else {
                console.warn('[fetchPrediction] ❌ Cannot save to history - missing required fields:', {
                    hasStatus: !!prediction?.status,
                    hasAlasan: !!prediction?.alasan
                });
            }

            // Navigasi ke halaman hasil
            navigate('/result', { state: { prediction, topic } });
        } catch (error) {
            console.error('Gagal mengambil prediksi:', error);
            alert('Gagal mengambil prediksi.');
        } finally {
            setLoading(false);
        }
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
        risk_level?: string;
        risk_label?: string;
        risk_color?: string;
    };

    type HistoryItem = {
        tanggal: string;
        customer_id: string;
        nama: string;
        topik: string;
        status: string;
        alasan: string;
        estimasi_pembayaran?: string;
        risk_level?: string;
        risk_label?: string;
        risk_color?: string;
    };

    // --- HELPER COMPONENTS ---


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
    const ScenarioControls = ({ topic, setTopic, isGenerating, disabled }: {
        topic: Topic;
        setTopic: (topic: Topic) => void;
        isGenerating: boolean;
        disabled: boolean;
    }) => {
        const navigate = useNavigate();
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
            <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-200 flex flex-col h-full">
                <div className="flex items-center gap-3 mb-4">
                    <Settings className="w-6 h-6 text-blue-600" />
                    <h3 className="text-lg font-bold text-gray-800">Pengaturan Skenario</h3>
                </div>
                <div className="mb-5">
                    <label className="block text-sm font-medium text-gray-600 mb-2 mt-2">Pilih Topik Simulasi</label>
                    <CustomDropdown
                        options={TOPICS}
                        selected={topic}
                        onSelect={(key) => setTopic(key as Topic)}
                        disabled={disabled || locked}
                    />
                </div>
                <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 mb-4">
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
                <div className="mt-auto">
                    <button
                        onClick={() => navigate('/Home')}
                        className="w-full flex items-center justify-center gap-2 px-5 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg shadow transition-all text-base"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2h4a2 2 0 012 2v1" /></svg>
                        Keluar Simulasi
                    </button>
                </div>
            </div>
        );
    };

    // Ganti AnswerInput agar mendukung closing







    // --- APP COMPONENT ---



    const handleStatusDihubungi = async (status: string) => {
        setLoading(true);
        const customer_id = sessionStorage.getItem('customer_id') || "";
        const token = sessionStorage.getItem('token');
        try {
            // Kirim status ke backend
            await fetch(`${API_BASE_URL}/conversation/update-status-dihubungi`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                },
                body: JSON.stringify({ customer_id, status }),
            });
            setStatusDihubungi(status);
            // Setelah status dihubungi, mulai chat AI dengan ucapan pembuka
            const user_email = sessionStorage.getItem('user_email') || '';
            // Debug: Check session data
            console.log('Starting conversation with:', { customer_id, topic, user_email });
            const response = await fetch(`${API_BASE_URL}/conversation/generate-simulation-questions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                },
                body: JSON.stringify({ customer_id, topic, conversation: [], user: user_email }),
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            const data = await response.json();
            if (data.question) {
                setCurrentQuestion({ q: data.question, options: data.options || [], is_closing: data.is_closing, question_followup: data.question_followup });
            }
        } catch (error) {
            console.error("Error in handleStatusDihubungi:", error);
            alert(`❌ Gagal memulai chat AI: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setLoading(false);
        }
    };

    const handleAnswer = async (answer: string) => {
        setLoading(true);
        // Clear current question immediately to show loading state
        const prevQuestion = currentQuestion;
        setCurrentQuestion(null);
        
        let newConversation;
        const customer_id = sessionStorage.getItem('customer_id') || "";
        const token = sessionStorage.getItem('token');
        const user_email = sessionStorage.getItem('user_email') || '';
        
        // Jawaban untuk pertanyaan AI saja
        if (
            prevQuestion?.q &&
            !(conversation.length > 0 && conversation[conversation.length - 1].q === prevQuestion.q && conversation[conversation.length - 1].a === answer)
        ) {
            newConversation = [...conversation, { q: prevQuestion.q, a: answer }];
            setConversation(newConversation);
        } else {
            newConversation = [...conversation];
        }
        
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

            // Generate pertanyaan berikutnya dengan Ollama
            console.log('🤖 Generating next question with Ollama...');
            const response = await fetch(`${API_BASE_URL}/conversation/generate-simulation-questions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                },
                body: JSON.stringify({ 
                    customer_id, 
                    topic, 
                    conversation: newConversation, 
                    user: user_email 
                }),
            });
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            console.log('🤖 Ollama response:', data);
            // Handle response from Ollama
            if (data.question) {
                console.log('✅ Setting new question from Ollama:', data.question);
                setCurrentQuestion({ 
                    q: data.question, 
                    options: data.options || [], 
                    is_closing: data.is_closing || data.stage === 'closing',
                    question_followup: data.question_followup
                });
            } else if (data.is_closing || data.stage === 'closing' || data.is_last) {
                // End conversation and get prediction
                console.log('🏁 Conversation ending, getting prediction...');
                
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
                        console.log('📊 Prediction result:', prediction);
                    }
                }
                
                setResult(prediction);
                
                // Simpan ke history SEBELUM navigate
                console.log('🎯 About to save prediction to history:');
                console.log('🎯 prediction object:', prediction);
                console.log('🎯 prediction.status:', prediction?.status);
                console.log('🎯 prediction.alasan:', prediction?.alasan);
                console.log('🎯 prediction.estimasi_pembayaran:', prediction?.estimasi_pembayaran);
                console.log('🎯 current topic:', topic);
                
                if (prediction && prediction.status && prediction.alasan) {
                    console.log('✅ Prediction is valid, calling addToSimulationHistory...');
                    addToSimulationHistory({
                        status: prediction.status,
                        alasan: prediction.alasan,
                        estimasi_pembayaran: prediction.estimasi_pembayaran || '-'
                    });
                    console.log('✅ History save completed, now navigating...');
                } else {
                    console.warn('❌ Prediction validation failed:', {
                        hasPrediction: !!prediction,
                        hasStatus: !!(prediction && prediction.status),
                        hasAlasan: !!(prediction && prediction.alasan)
                    });
                }
                
                // Navigate SETELAH history disimpan dengan delay kecil untuk memastikan
                setTimeout(() => {
                    navigate('/result', { state: { prediction, topic } });
                }, 100);
                setCurrentQuestion(null);
            } else {
                // No more questions available, end conversation
                setCurrentQuestion(null);
            }
        } catch (error) {
            console.error('❌ Error in handleAnswer:', error);
            
            // Restore previous question if generation failed
            if (prevQuestion) {
                setCurrentQuestion(prevQuestion);
            }
            
            // Show user-friendly error message
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            if (errorMessage.includes('Ollama') || errorMessage.includes('generate')) {
                alert("⚠️ AI generation temporarily unavailable. Using fallback questions.\n\nThe system will continue with standard question flow.");
            } else {
                alert("❌ Gagal mengambil pertanyaan berikutnya. Silakan coba lagi.");
            }
        } finally {
            setLoading(false);
        }
    };

    const handleBack = async () => {
        if (conversation.length > 0) {
            // Hapus percakapan terakhir
            const newConversation = conversation.slice(0, -1);
            setConversation(newConversation);
            
            // Kosongkan prediksi terakhir (kalau ada)
            // setPrediction(null); // Removed as setPrediction is no longer available
            
            // Generate pertanyaan sebelumnya berdasarkan conversation yang tersisa
            try {
                setLoading(true);
                const customer_id = sessionStorage.getItem('customer_id') || "";
                const token = sessionStorage.getItem('token');
                const user_email = sessionStorage.getItem('user_email') || '';
                
                const response = await fetch(`${API_BASE_URL}/conversation/generate-simulation-questions`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(token ? { Authorization: `Bearer ${token}` } : {})
                    },
                    body: JSON.stringify({ 
                        customer_id, 
                        topic, 
                        conversation: newConversation, 
                        user: user_email 
                    }),
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.question) {
                        setCurrentQuestion({ 
                            q: data.question, 
                            options: data.options || [], 
                            is_closing: data.is_closing 
                        });
                    }
                } else {
                    // Jika gagal mendapatkan pertanyaan, kembali ke pertanyaan awal
                    if (newConversation.length === 0) {
                        const initialResponse = await fetch(`${API_BASE_URL}/conversation/generate-simulation-questions`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                ...(token ? { Authorization: `Bearer ${token}` } : {})
                            },
                            body: JSON.stringify({ 
                                customer_id, 
                                topic, 
                                conversation: [], 
                                user: user_email 
                            }),
                        });
                        
                        if (initialResponse.ok) {
                            const initialData = await initialResponse.json();
                            if (initialData.question) {
                                setCurrentQuestion({ 
                                    q: initialData.question, 
                                    options: initialData.options || [], 
                                    is_closing: initialData.is_closing 
                                });
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Error getting previous question:', error);
                // Fallback: jika error, setidaknya bersihkan current question
                if (newConversation.length === 0) {
                    setCurrentQuestion(null);
                }
            } finally {
                setLoading(false);
            }
        } else {
            alert("Tidak ada pertanyaan sebelumnya.");
        }
    };






    const isSimulationRunning = currentQuestion !== null && !result;

    // Ambil nama dari sessionStorage
    const customerName = sessionStorage.getItem('customer_name') || '';
    const getInitials = (name: string) => {
        if (!name) return '';
        return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
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
                                isGenerating={false}
                                disabled={isSimulationRunning}
                            />
                        </div>
                    </aside>
                    <div className="lg:col-span-8 xl:col-span-9 flex flex-col gap-8">
                        {/* Status Dihubungi Selalu di Atas Kolom Pertanyaan AI */}
                        <div>
                            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 flex flex-col sm:flex-row items-center justify-between gap-6">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2h4a2 2 0 012 2v1" /></svg>
                                    </div>
                                    <div>
                                        <h2 className="text-lg font-bold text-gray-800 mb-1">Status Dihubungi</h2>
                                        <p className="text-gray-500 text-sm">Pilih status pelanggan sebelum memulai simulasi AI.</p>
                                    </div>
                                </div>
                                <div className="flex gap-4 mt-6">
                                    <button
                                        onClick={() => handleStatusDihubungi("Dihubungi")}
                                        disabled={loading || statusDihubungi === "Dihubungi"}
                                        className={`px-6 py-3 rounded-lg font-semibold shadow transition-all duration-150 ${
                                            statusDihubungi === "Dihubungi"
                                                ? "bg-green-600 text-white"
                                                : "bg-gray-100 hover:bg-green-50 text-gray-700"
                                        }`}
                                    >
                                        Dihubungi
                                    </button>

                                    <button
                                        onClick={() => {
                                            setShowAlasanTidakDihubungi(true);
                                            setStatusDihubungi("Tidak Dihubungi");
                                            setCurrentQuestion(null); // Hilangkan kolom pertanyaan AI
                                        }}
                                        disabled={loading || statusDihubungi === "Tidak Dihubungi"}
                                        className={`px-6 py-3 rounded-lg font-semibold shadow transition-all duration-150 ${
                                            statusDihubungi === "Tidak Dihubungi"
                                                ? "bg-red-600 text-white"
                                                : "bg-gray-100 hover:bg-red-50 text-gray-700"
                                        }`}
                                    >
                                        Tidak Dihubungi
                                    </button>
                                </div>
                            </div>
                            {showAlasanTidakDihubungi && (
                                <div className="mt-4">
                                    <p className="font-semibold mb-2">Pilih alasan tidak dapat dihubungi:</p>
                                    {alasanOptions.map((alasan) => (
                                        <label key={alasan} className="block mb-2">
                                            <input
                                                type="radio"
                                                name="alasan"
                                                value={alasan}
                                                checked={selectedAlasan === alasan}
                                                onChange={() => setSelectedAlasan(alasan)}
                                            />
                                            <span className="ml-2">{alasan}</span>
                                        </label>
                                    ))}
                                    <button
                                        className="mt-2 px-4 py-2 bg-blue-600 text-white rounded"
                                        disabled={!selectedAlasan}
                                        onClick={() => {
                                            // Simpan ke history untuk Tidak Dapat Dihubungi hanya jika data valid
                                            if (selectedAlasan && topic) {
                                                addToSimulationHistory({
                                                    status: `Tidak Dihubungi`,
                                                    alasan: selectedAlasan,
                                                    estimasi_pembayaran: "-"
                                                });
                                            }
                                            
                                            handleStatusDihubungi(`Tidak Dihubungi: ${selectedAlasan}`);
                                            setShowAlasanTidakDihubungi(false);
                                            navigate('/customer-reason', {
                                                state: {
                                                    customerName,
                                                    customerId: sessionStorage.getItem('customer_id') || '-',
                                                    topic,
                                                    alasan: selectedAlasan
                                                }
                                            });
                                            setSelectedAlasan(null);
                                        }}
                                    >
                                        Konfirmasi Alasan
                                    </button>
                                    {/* Tambahkan tombol batal di sini */}
                                    <button
                                        className="mt-2 ml-2 px-4 py-2 bg-gray-300 text-gray-700 rounded"
                                        onClick={() => {
                                            setShowAlasanTidakDihubungi(false);
                                            setSelectedAlasan(null);
                                        }}
                                    >
                                        Batal
                                    </button>
                                </div>
                            )}
                        </div>
                        {/* Halaman CustomerReasonPage sekarang diakses via route, tidak perlu render di sini */}
                        {/* Tampilkan kolom pertanyaan AI hanya jika status dihubungi (bukan tidak dihubungi) */}
                        {statusDihubungi && statusDihubungi === 'Dihubungi' && currentQuestion && (
                            <>
                                <QuestionBox
                                    question={currentQuestion.q}
                                    options={currentQuestion.options}
                                    loading={loading}
                                    isClosing={!!currentQuestion.is_closing}
                                    onAnswer={(answer, closing) => {
                                        if (closing) {
                                            fetchPrediction(); // langsung ke halaman hasil prediksi
                                        } else {
                                            handleAnswer(answer);
                                        }
                                    }}
                                />
                                {/* Tombol Navigasi Pertanyaan AI */}
                                <div className="mt-4 flex justify-between items-center">
                                    <button
                                        className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition-all"
                                        onClick={handleBack}
                                        disabled={loading || conversation.length === 0}
                                    >
                                        ← Back
                                    </button>
                                    <button
                                        className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-all"
                                        onClick={() => {
                                            setStatusDihubungi(null);
                                            setCurrentQuestion(null);
                                            setConversation([]);
                                        }}
                                        disabled={loading}
                                    >
                                        Batal
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </main>


        </div>
    );
};


export default CSSimulation;
// QuestionBox dipindahkan menjadi export biasa, tanpa export default kedua

interface QuestionBoxProps {
    question: string;
    options?: string[];
    loading: boolean;
    isClosing: boolean;
    onAnswer: (answer: string, closing: boolean) => void;
}

export function QuestionBox({
    question,
    options = [],
    loading,
    isClosing,
    onAnswer,
    ...rest
}: QuestionBoxProps & { question_followup?: string }) {
    const [manualAnswer, setManualAnswer] = useState("");

    // Support for split winback question
    const questionFollowup = rest.question_followup;

    // Jika closing, hanya tampilkan kalimat penutup dan tombol Selesai
    if (isClosing) {
        return (
            <div className="w-full bg-white/80 backdrop-blur-lg p-6 rounded-2xl shadow-xl border border-gray-200 space-y-5 flex flex-col items-center">
                <p className="text-xl font-semibold text-gray-800 mb-6" style={{ fontFamily: 'Times New Roman, Times, serif', whiteSpace: 'pre-line', lineHeight: '1.6', textAlign: 'center' }}>{question}</p>
                <button
                    className="w-full py-3 bg-blue-600 text-white font-bold rounded-xl shadow-lg text-lg transition-all hover:bg-blue-700"
                    onClick={() => onAnswer("Selesai", true)}
                    disabled={loading}
                >
                    Selesai
                </button>
            </div>
        );
    }
    let limitedOptions: string[] = [];
    if (Array.isArray(options) && options.length > 0) {
        limitedOptions = options.slice(0, 4);
    }
    const handleManualSubmit = () => {
        if (manualAnswer.trim()) {
            onAnswer(manualAnswer, false);
            setManualAnswer("");
        }
    };
    return (
        <div className="w-full bg-white/80 backdrop-blur-lg p-6 rounded-2xl shadow-xl border border-gray-200 space-y-5">
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
                    {questionFollowup && (
                        <span style={{ display: 'block', marginTop: '12px', color: '#444', fontWeight: 500 }}>{questionFollowup}</span>
                    )}
                </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {limitedOptions.map((opt, i) => (
                    <button
                        key={i}
                        onClick={() => onAnswer(opt, false)}
                        disabled={loading}
                        className="text-left p-4 bg-white hover:bg-blue-50 border border-gray-300 rounded-lg transition-all duration-200 disabled:opacity-50 hover:border-blue-400 hover:shadow-md font-medium text-gray-700"
                    >
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

                <button
                    onClick={handleManualSubmit}
                    disabled={loading || !manualAnswer.trim()}
                    className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all disabled:bg-gray-400"
                >
                    {loading ? 'Memproses...' : 'Lanjutkan'}
                </button>
            </div>
        </div>
    );
}

