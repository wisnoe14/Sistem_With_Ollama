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
    Zap,
} from 'lucide-react';
// Fungsi untuk memanggil intent OpenAI
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1/endpoints";




const CSSimulation = () => {
    const navigate = useNavigate();
    
    // Validasi customer_id di awal - redirect jika tidak ada
    useEffect(() => {
        const customerId = sessionStorage.getItem('customer_id');
        if (!customerId || customerId.trim() === '' || customerId === '-') {
            console.warn('⚠️ Customer ID tidak ditemukan, redirect ke Home');
            navigate('/Home');
        }
    }, [navigate]);
    
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
    const [loading, setLoading] = useState(false);
    const dedupeWindowMs = 10000;
    const getHistoryTime = (item: HistoryItem) => {
        if (typeof item.timestamp === 'number') {
            return item.timestamp;
        }
        const parsed = new Date(item.tanggal).getTime();
        return Number.isNaN(parsed) ? 0 : parsed;
    };

    const [, setConversationHistory] = useState<HistoryItem[]>(() => {
        const saved = localStorage.getItem('conversationHistory');
        const history = saved ? JSON.parse(saved) : [];
        
        // Remove duplicates on load
        const uniqueHistory = history.filter((item: HistoryItem, index: number) => {
            // Keep item if no duplicate found in previous items
            return !history.slice(0, index).some((prevItem: HistoryItem) => 
                prevItem.customer_id === item.customer_id &&
                prevItem.topik === item.topik &&
                prevItem.status === item.status &&
                prevItem.alasan === item.alasan &&
                Math.abs(getHistoryTime(prevItem) - getHistoryTime(item)) < dedupeWindowMs
            );
        });
        
        if (uniqueHistory.length !== history.length) {
            localStorage.setItem('conversationHistory', JSON.stringify(uniqueHistory));
        }
        
        return uniqueHistory;
    });

    // Helper untuk menambah data ke history dengan format tabel
    function addToConversationHistory({ status, alasan, estimasi_pembayaran, risk_level, risk_label, risk_color }: { status: string; alasan: string; estimasi_pembayaran?: string; risk_level?: string; risk_label?: string; risk_color?: string }) {
        console.log('[addToConversationHistory] 📝 Called with:', { status, alasan, estimasi_pembayaran, risk_level, risk_label, risk_color });
        console.log('[addToConversationHistory] Current topic state:', topic);
        
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
        const timestamp = now.getTime();
        const tanggal = now.toLocaleDateString('id-ID') + ', ' + now.toLocaleTimeString('id-ID');
        const customer_id = sessionStorage.getItem('customer_id') || '-';
        const nama = sessionStorage.getItem('customer_name') || '-';
        const topik = topic;
    const item = { tanggal, timestamp, customer_id, nama, topik, status, alasan, estimasi_pembayaran: estimasi_pembayaran || '-', risk_level: risk_level || 'low', risk_label: risk_label || 'Aman', risk_color: risk_color || '#16a34a' };
        
        // Debug: Log data yang akan disimpan
        console.log('💾 Saving to history:', item);
        console.log('💾 Current topic:', topic);
        console.log('💾 Status received:', status);
        console.log('💾 Alasan received:', alasan);
        console.log('🎯 Risk Level:', risk_level);
        console.log('🎯 Risk Label:', risk_label);
        console.log('🎯 Risk Color:', risk_color);
        
        setConversationHistory(prev => {
            const isDuplicate = prev.some((entry) => (
                entry.customer_id === customer_id &&
                entry.topik === topik &&
                entry.status === status &&
                entry.alasan === alasan &&
                Math.abs(getHistoryTime(entry) - timestamp) < dedupeWindowMs
            ));

            if (isDuplicate) {
                console.log('🚫 Preventing duplicate history entry');
                return prev;
            }
            
            const updated = [item, ...prev];
            localStorage.setItem('conversationHistory', JSON.stringify(updated));
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
    options: string[] | Array<{ text: string; next_question: string; action: string }>;
    is_closing?: boolean;
    question_followup?: string;
    question_id?: string;
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
                addToConversationHistory({
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
        question_id?: string;
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
        timestamp?: number;
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


    // Ganti AnswerInput agar mendukung closing







    // --- APP COMPONENT ---



    const handleStatusDihubungi = async (status: string) => {
        setLoading(true);
        if (status === "Dihubungi") {
            setShowAlasanTidakDihubungi(false);
            setSelectedAlasan(null);
        }
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
            const response = await fetch(`${API_BASE_URL}/conversation/cs-chatbot/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                },
                body: JSON.stringify({ mode: topic, conversation_history: [] }),
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            const data = await response.json();
            if (data.question) {
                const questionData = data.question || {};
                setCurrentQuestion({ 
                    q: questionData.question, 
                    options: questionData.options || [], 
                    is_closing: questionData.is_closing, 
                    question_followup: data.question_followup,
                    question_id: questionData.question_id
                });
            }
        } catch (error) {
            console.error("Error in handleStatusDihubungi:", error);
            alert(`❌ Gagal memulai chat AI: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setLoading(false);
        }
    };

    const handleAnswer = async (answer: string) => {
        console.log('🎯 handleAnswer called with answer:', answer);
        setLoading(true);
        // Clear current question immediately to show loading state
        const prevQuestion = currentQuestion;
        const isClosingAnswer = prevQuestion?.is_closing === true;
        
        console.log('📋 Current question state:', {
            hasQuestion: !!prevQuestion,
            isClosing: prevQuestion?.is_closing,
            isClosingAnswer: isClosingAnswer,
            questionText: prevQuestion?.q?.substring(0, 50) + '...'
        });
        
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
            newConversation = [...conversation, { 
                q: prevQuestion.q, 
                a: answer,
                question_id: prevQuestion?.question_id 
            }];
            setConversation(newConversation);
        } else {
            newConversation = [...conversation];
        }
        
        try {
            // Simpan percakapan ke backend
            const saveRes = await fetch(`${API_BASE_URL}/conversation/cs-chatbot/next-question`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                },
                body: JSON.stringify({ 
                    mode: topic, 
                    question_id: prevQuestion?.question_id || 'opening',
                    selected_answer: answer,
                    conversation_history: newConversation.map(conv => ({
                        q: conv.q,
                        a: conv.a,
                        question_id: conv.question_id
                    })),
                    customer_id 
                }),
            });
            if (!saveRes.ok) throw new Error('Gagal menyimpan percakapan');
            const saveData = await saveRes.json();
            if (!saveData.success) throw new Error(saveData.error || 'Gagal menyimpan percakapan');
            
            // Update current question with response
            if (saveData.next_question) {
                const nextQ = saveData.next_question;
                setCurrentQuestion({
                    q: nextQ.question || nextQ.q,
                    options: nextQ.options || [],
                    is_closing: nextQ.is_closing,
                    question_id: nextQ.question_id
                });
            }

            // 🎯 JIKA SELESAI/CLOSING, LANGSUNG KE PREDICTION - SKIP GENERATE QUESTION
            if (isClosingAnswer) {
                console.log('✅ CLOSING DETECTED! Going directly to prediction...');
                console.log('🚫 SKIPPING question generation!');
                
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
                
                let prediction = null;
                if (predictRes.ok) {
                    const predictData = await predictRes.json();
                    if (predictData && predictData.result) {
                        prediction = predictData.result;
                        console.log('📊 Prediction result:', prediction);
                    }
                }
                
                setResult(prediction);
                
                // Simpan ke history
                if (prediction && prediction.status && prediction.alasan) {
                    console.log('✅ Prediction is valid, calling addToConversationHistory...');
                    addToConversationHistory({
                        status: prediction.status,
                        alasan: prediction.alasan,
                        estimasi_pembayaran: prediction.estimasi_pembayaran || '-'
                    });
                    console.log('✅ History save completed, now navigating...');
                }
                
                // Navigate ke result page
                setTimeout(() => {
                    navigate('/result', { state: { prediction, topic } });
                }, 100);
                
                setCurrentQuestion(null);
                setLoading(false);
                return; // Exit early
            }

            // Generate pertanyaan berikutnya dengan sistem baru
            console.log('🤖 Generating next question with new system...');
            const response = await fetch(`${API_BASE_URL}/conversation/cs-chatbot/next-question`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                },
                body: JSON.stringify({ 
                    mode: topic,
                    question_id: prevQuestion?.question_id || 'opening',
                    selected_answer: answer,
                    conversation_history: newConversation.map(conv => ({
                        q: conv.q,
                        a: conv.a,
                        question_id: conv.question_id
                    })),
                    customer_id 
                }),
            });
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            console.log('🤖 System response:', data);
            // Handle response from system
            if (data.next_question) {
                const nextQ = data.next_question;
                console.log('✅ Setting new question from system:', nextQ.question);
                setCurrentQuestion({ 
                    q: nextQ.question, 
                    options: nextQ.options || [], 
                    is_closing: nextQ.is_closing,
                    question_id: nextQ.question_id
                });
            } else if (data.is_closing || data.next_question?.is_closing) {
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
                    console.log('✅ Prediction is valid, calling addToConversationHistory...');
                    addToConversationHistory({
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
                
                const response = await fetch(`${API_BASE_URL}/conversation/cs-chatbot/next-question`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...(token ? { Authorization: `Bearer ${token}` } : {})
                    },
                    body: JSON.stringify({ 
                        mode: topic,
                        question_id: currentQuestion?.question_id || 'opening',
                        selected_answer: '',
                        conversation_history: newConversation.map(conv => ({
                            q: conv.q,
                            a: conv.a,
                            question_id: conv.question_id
                        })),
                        customer_id 
                    }),
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.next_question) {
                        const nextQ = data.next_question;
                        setCurrentQuestion({ 
                            q: nextQ.question, 
                            options: nextQ.options || [], 
                            is_closing: nextQ.is_closing,
                            question_id: nextQ.question_id
                        });
                    }
                } else {
                    // Jika gagal mendapatkan pertanyaan, kembali ke pertanyaan awal
                    if (newConversation.length === 0) {
                        const initialResponse = await fetch(`${API_BASE_URL}/conversation/cs-chatbot/start`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                ...(token ? { Authorization: `Bearer ${token}` } : {})
                            },
                            body: JSON.stringify({ mode: topic, conversation_history: [] }),
                        });
                        
                        if (initialResponse.ok) {
                            const initialData = await initialResponse.json();
                            if (initialData.question) {
                                const initQ = initialData.question || {};
                                setCurrentQuestion({ 
                                    q: initQ.question,
                                    options: initQ.options || [], 
                                    is_closing: initQ.is_closing,
                                    question_id: initQ.question_id
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
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 relative overflow-hidden" style={{ fontFamily: "'Inter', 'Poppins', sans-serif" }}>
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -left-40 w-80 h-80 bg-blue-500/10 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blob"></div>
                <div className="absolute -top-40 right-0 w-80 h-80 bg-cyan-500/10 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blob animation-delay-2000"></div>
                <div className="absolute bottom-0 left-20 w-80 h-80 bg-indigo-500/10 rounded-full mix-blend-screen filter blur-3xl opacity-40 animate-blob animation-delay-4000"></div>
            </div>

            <div className="relative z-10">
                <header className="sticky top-0 z-50 bg-white/5 backdrop-blur-xl border-b border-white/10 shadow-lg">
                    <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                        <div className="flex items-center justify-between h-20">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-blue-600 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
                                    <Bot className="w-7 h-7 text-white" />
                                </div>
                                <div>
                                    <h1 className="text-xl font-bold bg-gradient-to-r from-blue-300 to-cyan-300 bg-clip-text text-transparent">
                                        ICONNET AI Assistant
                                    </h1>
                                    <p className="text-xs text-blue-300/70">Sistem AI untuk Layanan Pelanggan</p>
                                </div>
                            </div>
                            {customerName && (
                                <div className="flex items-center gap-3 px-5 py-2.5 bg-white/10 border border-white/20 rounded-xl backdrop-blur-sm hover:bg-white/20 transition-all duration-200">
                                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-lg">
                                        {getInitials(customerName)}
                                    </div>
                                    <div className="hidden sm:block">
                                        <p className="text-sm font-semibold text-white">{customerName}</p>
                                        <p className="text-xs text-blue-300/70">{sessionStorage.getItem('customer_id')}</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </header>

                <main className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
                        <aside className="lg:col-span-4 xl:col-span-3">
                            <div className="lg:sticky lg:top-28">
                                <div className="bg-gradient-to-br from-white to-blue-50/50 p-8 rounded-3xl shadow-2xl border border-gray-100 backdrop-blur-sm">
                                    <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 px-6 py-6 -m-8 mb-6 rounded-t-3xl relative overflow-hidden">
                                        <div className="absolute inset-0 opacity-10">
                                            <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full filter blur-2xl"></div>
                                        </div>
                                        <div className="flex items-center gap-3 relative z-10">
                                            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                                                <Settings className="w-6 h-6 text-white" />
                                            </div>
                                            <div>
                                                <h3 className="text-xl font-bold text-white">Pengaturan Skenario</h3>
                                                <p className="text-blue-100 text-xs">Pilih topik percakapan</p>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-5">
                                        <div>
                                            <label className="block text-sm font-bold text-gray-700 mb-3">Topik Percakapan <span className="text-red-500">*</span></label>
                                            <CustomDropdown
                                                options={[
                                                    { key: "telecollection", label: "Telecollection", icon: CreditCard },
                                                    { key: "retention", label: "Retention", icon: ShieldCheck },
                                                    { key: "winback", label: "Winback", icon: Target },
                                                ]}
                                                selected={topic}
                                                onSelect={(key) => setTopic(key as Topic)}
                                                disabled={isSimulationRunning}
                                            />
                                        </div>

                                        <div className="p-5 bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-2xl">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm">
                                                    {topic === "telecollection" && <CreditCard className="w-5 h-5 text-blue-600" />}
                                                    {topic === "retention" && <ShieldCheck className="w-5 h-5 text-blue-600" />}
                                                    {topic === "winback" && <Target className="w-5 h-5 text-blue-600" />}
                                                </div>
                                                <div>
                                                    <h4 className="font-bold text-gray-800 capitalize">{topic}</h4>
                                                    <p className="text-xs text-gray-600">
                                                        {topic === "telecollection" && "Penagihan & Recovery"}
                                                        {topic === "retention" && "Pencegahan Churn"}
                                                        {topic === "winback" && "Reaktivasi Customer"}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>

                                        <button
                                            onClick={() => navigate('/Home')}
                                            className="w-full mt-6 flex items-center justify-center gap-2 px-5 py-4 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-bold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 active:scale-95"
                                        >
                                            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2h4a2 2 0 012 2v1" /></svg>
                                            Keluar Percakapan
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </aside>

                        <div className="lg:col-span-8 xl:col-span-9 flex flex-col gap-8">
                            <div className="bg-gradient-to-br from-white to-blue-50/50 rounded-3xl shadow-2xl border border-gray-100 backdrop-blur-sm overflow-hidden">
                                <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 px-8 py-6 relative overflow-hidden">
                                    <div className="absolute inset-0 opacity-10">
                                        <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full filter blur-2xl"></div>
                                    </div>
                                    <div className="flex items-center gap-4 relative z-10">
                                        <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center shadow-xl">
                                            <svg xmlns="http://www.w3.org/2000/svg" className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2h4a2 2 0 012 2v1" /></svg>
                                        </div>
                                        <div>
                                            <h2 className="text-2xl font-bold text-white">Status Dihubungi</h2>
                                            <p className="text-blue-100 text-sm mt-1">Pilih status pelanggan untuk memulai percakapan</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="p-8 space-y-6">
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        <button
                                            onClick={() => handleStatusDihubungi("Dihubungi")}
                                            disabled={loading || statusDihubungi === "Dihubungi"}
                                            className={`px-6 py-4 rounded-xl font-bold text-base shadow-lg transition-all duration-300 transform hover:-translate-y-0.5 active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none ${
                                                statusDihubungi === "Dihubungi"
                                                    ? "bg-gradient-to-r from-green-600 to-green-700 text-white"
                                                    : "bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 hover:from-green-50 hover:to-green-100"
                                            }`}
                                        >
                                            ✓ Dihubungi
                                        </button>

                                        <button
                                            onClick={() => {
                                                setShowAlasanTidakDihubungi(true);
                                                setStatusDihubungi("Tidak Dihubungi");
                                                setCurrentQuestion(null);
                                            }}
                                            disabled={loading || statusDihubungi === "Tidak Dihubungi"}
                                            className={`px-6 py-4 rounded-xl font-bold text-base shadow-lg transition-all duration-300 transform hover:-translate-y-0.5 active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none ${
                                                statusDihubungi === "Tidak Dihubungi"
                                                    ? "bg-gradient-to-r from-red-600 to-red-700 text-white"
                                                    : "bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 hover:from-red-50 hover:to-red-100"
                                            }`}
                                        >
                                            ✗ Tidak Dihubungi
                                        </button>
                                    </div>

                                    {showAlasanTidakDihubungi && (
                                        <div className="p-5 bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-2xl space-y-3 animate-in fade-in slide-in-from-top">
                                            <p className="font-bold text-gray-800 text-sm">Pilih alasan tidak dapat dihubungi:</p>
                                            <div className="space-y-2">
                                                {alasanOptions.map((alasan) => (
                                                    <label key={alasan} className="flex items-center gap-3 p-3 bg-white rounded-xl cursor-pointer hover:bg-red-50 transition-colors duration-150 border border-red-100">
                                                        <input
                                                            type="radio"
                                                            name="alasan"
                                                            value={alasan}
                                                            checked={selectedAlasan === alasan}
                                                            onChange={() => setSelectedAlasan(alasan)}
                                                            className="w-4 h-4"
                                                        />
                                                        <span className="font-medium text-gray-700">{alasan}</span>
                                                    </label>
                                                ))}
                                            </div>
                                            <div className="flex gap-3 pt-2">
                                                <button
                                                    className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold rounded-xl shadow transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                                    disabled={!selectedAlasan}
                                                    onClick={() => {
                                                        if (selectedAlasan && topic) {
                                                            addToConversationHistory({
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
                                                    Konfirmasi
                                                </button>
                                                <button
                                                    className="flex-1 px-4 py-3 bg-gradient-to-r from-gray-400 to-gray-500 hover:from-gray-500 hover:to-gray-600 text-white font-bold rounded-xl shadow transition-all"
                                                    onClick={() => {
                                                        setShowAlasanTidakDihubungi(false);
                                                        setSelectedAlasan(null);
                                                    }}
                                                >
                                                    Batal
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
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
        </div>
    );
};


export default CSSimulation;

// QuickRepliesModalContent component
interface QuickRepliesModalContentProps {
    onSelect: (reply: string) => void;
}

function QuickRepliesModalContent({ onSelect }: QuickRepliesModalContentProps) {
    const quickReplies = [
        { id: 1, category: 'Greeting', title: 'Greeting', content: 'Selamat pagi/siang/malam, saya dari tim customer service ICONNET. Bagaimana kabar Anda?' },
        { id: 2, category: 'Retention', title: 'Penawaran Khusus', content: 'Kami memiliki penawaran menarik khusus untuk pelanggan setia seperti Anda. Apakah Anda tertarik mendengar lebih lanjut?' },
        { id: 3, category: 'Collections', title: 'Pengingat Pembayaran', content: 'Kami mengingatkan bahwa ada tagihan yang belum dibayarkan. Bisakah kami membantu mengatur rencana pembayaran?' },
        { id: 4, category: 'Technical', title: 'Bantuan Teknis', content: 'Jika Anda mengalami masalah teknis, kami siap membantu. Bisa Anda jelaskan masalahnya?' },
        { id: 5, category: 'Follow-up', title: 'Tindak Lanjut', content: 'Terima kasih telah memberikan informasinya. Mari kami lanjutkan percakapan ini.' },
        { id: 6, category: 'Closing', title: 'Penutupan', content: 'Terima kasih telah meluangkan waktu. Jika ada yang bisa kami bantu, jangan ragu untuk menghubungi kami.' },
        { id: 7, category: 'Empathy', title: 'Empati', content: 'Kami mengerti situasi Anda. Mari bersama-sama mencari solusi terbaik untuk kebutuhan Anda.' },
        { id: 8, category: 'Escalation', title: 'Eskalasi', content: 'Saya akan menghubungkan Anda dengan supervisor kami untuk penanganan yang lebih lanjut.' },
        { id: 9, category: 'Feedback', title: 'Permintaan Feedback', content: 'Apakah kami dapat menerima feedback dari Anda tentang layanan kami? Masukan Anda sangat berharga.' },
        { id: 10, category: 'Winback', title: 'Penawaran Reaktivasi', content: 'Kami merindu kehadiran Anda. Dapatkan bonus khusus jika Anda reaktivasi layanan Anda hari ini!' },
    ];

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {quickReplies.map((reply) => (
                <button
                    key={reply.id}
                    onClick={() => onSelect(reply.content)}
                    className="text-left p-3 bg-gradient-to-br from-amber-50 to-orange-50 hover:from-amber-100 hover:to-orange-100 border border-amber-200 rounded-lg transition-all duration-200 hover:shadow-md hover:border-amber-400 group"
                >
                    <div className="flex items-center gap-2 mb-1">
                        <span className="inline-block px-2 py-1 bg-amber-600 text-white text-xs font-bold rounded">
                            {reply.category.slice(0, 3).toUpperCase()}
                        </span>
                    </div>
                    <p className="font-semibold text-gray-800 text-sm mb-1 group-hover:text-amber-700">{reply.title}</p>
                    <p className="text-gray-600 text-xs line-clamp-2">{reply.content}</p>
                </button>
            ))}
        </div>
    );
}
// QuestionBox dipindahkan menjadi export biasa, tanpa export default kedua

interface QuestionBoxProps {
    question: string;
    options?: string[] | Array<{ text: string; next_question: string; action: string }>;
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
    const [showQuickReplies, setShowQuickReplies] = useState(false);

    // Support for split winback question
    const questionFollowup = rest.question_followup;

    // Handle selecting a quick reply
    const handleSelectQuickReply = (reply: string) => {
        setManualAnswer(prev => prev ? prev + '\n' + reply : reply);
        setShowQuickReplies(false);
    };

    // Jika closing, hanya tampilkan kalimat penutup dan tombol Selesai
    if (isClosing) {
        return (
            <div className="w-full bg-white/80 backdrop-blur-lg p-6 rounded-2xl shadow-xl border border-gray-200 space-y-5 flex flex-col items-center">
                <p className="text-xl font-semibold text-gray-800 mb-6" style={{ fontFamily: 'Times New Roman, Times, serif', whiteSpace: 'pre-line', lineHeight: '1.6', textAlign: 'center' }}>{question}</p>
                <button
                    className={`w-full py-3 font-bold rounded-xl shadow-lg text-lg transition-all ${
                        loading 
                            ? 'bg-gray-400 cursor-not-allowed' 
                            : 'bg-blue-600 hover:bg-blue-700 cursor-pointer'
                    } text-white flex items-center justify-center gap-2`}
                    onClick={() => !loading && onAnswer("Selesai", true)}
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span>Memproses Prediksi...</span>
                        </>
                    ) : (
                        <>
                            <span>✅ Selesai</span>
                        </>
                    )}
                </button>
            </div>
        );
    }
    let limitedOptions: any[] = [];
    if (Array.isArray(options) && options.length > 0) {
        limitedOptions = options.slice(0, 4);
    }
    
    // Helper function to get display text from option (handles both string and object formats)
    const getOptionText = (opt: any): string => {
        if (typeof opt === 'string') {
            return opt;
        }
        if (typeof opt === 'object' && opt?.text) {
            return opt.text;
        }
        return '';
    };
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
                {limitedOptions.map((opt, i) => {
                    const optionText = getOptionText(opt);
                    return (
                        <button
                            key={i}
                            onClick={() => onAnswer(optionText, false)}
                            disabled={loading}
                            className="text-left p-4 bg-white hover:bg-blue-50 border border-gray-300 rounded-lg transition-all duration-200 disabled:opacity-50 hover:border-blue-400 hover:shadow-md font-medium text-gray-700"
                        >
                            {optionText}
                        </button>
                    );
                })}
            </div>
            <div className="relative flex items-center">
                <hr className="w-full border-gray-300" />
                <span className="absolute left-1/2 -translate-x-1/2 bg-white/80 px-2 text-sm text-gray-500 font-medium">ATAU</span>
            </div>
            <div className="space-y-3">
                <div className="flex gap-2 items-center">
                    <button
                        onClick={() => setShowQuickReplies(true)}
                        className="flex items-center gap-2 px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white font-semibold rounded-lg shadow transition-all"
                        title="Lihat Template Respons Cepat"
                    >
                        <Zap className="w-4 h-4" />
                        <span className="text-sm">Quick Replies</span>
                    </button>
                    <span className="text-xs text-gray-500">atau tulis jawaban manual</span>
                </div>
                <textarea
                    className="w-full p-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none transition-shadow"
                    rows={3}
                    placeholder="Ketik jawaban manual di sini atau gunakan Quick Replies..."
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

                {/* Quick Replies Modal */}
                {showQuickReplies && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-96 overflow-y-auto">
                            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
                                <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                                    <Zap className="w-5 h-5 text-amber-600" />
                                    Pilih Respons Cepat
                                </h3>
                                <button
                                    onClick={() => setShowQuickReplies(false)}
                                    className="text-gray-500 hover:text-gray-700 font-bold"
                                >
                                    ✕
                                </button>
                            </div>
                            <div className="p-4 space-y-2">
                                <QuickRepliesModalContent onSelect={handleSelectQuickReply} />
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

