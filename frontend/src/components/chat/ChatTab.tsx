"use client";
import { useStore } from "@/lib/store";
import { useState, useRef, useEffect, useCallback } from "react";
import { Send, User, Bot, Sparkles, Volume2, VolumeX, Loader2, Mic, MicOff } from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { requestTTS } from "@/lib/api";

// Type declaration for Web Speech API
interface SpeechRecognitionEvent extends Event {
    results: SpeechRecognitionResultList;
    resultIndex: number;
}

interface SpeechRecognitionResultList {
    length: number;
    item(index: number): SpeechRecognitionResult;
    [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
    isFinal: boolean;
    length: number;
    item(index: number): SpeechRecognitionAlternative;
    [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
    transcript: string;
    confidence: number;
}

interface SpeechRecognition extends EventTarget {
    continuous: boolean;
    interimResults: boolean;
    lang: string;
    start(): void;
    stop(): void;
    abort(): void;
    onresult: ((event: SpeechRecognitionEvent) => void) | null;
    onerror: ((event: Event) => void) | null;
    onend: (() => void) | null;
    onstart: (() => void) | null;
}

declare global {
    interface Window {
        SpeechRecognition: new () => SpeechRecognition;
        webkitSpeechRecognition: new () => SpeechRecognition;
    }
}

export default function ChatTab() {
    const { chatHistory, sendMessage, isChatSending } = useStore();
    const [input, setInput] = useState("");
    const scrollRef = useRef<HTMLDivElement>(null);
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const [playingIdx, setPlayingIdx] = useState<number | null>(null);
    const [loadingIdx, setLoadingIdx] = useState<number | null>(null);

    // Speech Recognition State
    const [isListening, setIsListening] = useState(false);
    const [speechSupported, setSpeechSupported] = useState(false);
    const recognitionRef = useRef<SpeechRecognition | null>(null);
    const transcriptRef = useRef<string>(""); // Track transcript for auto-submit
    const [shouldAutoPlay, setShouldAutoPlay] = useState(false); // Auto-play response if voice was used

    // Check for speech recognition support on mount
    useEffect(() => {
        const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognitionAPI) {
            setSpeechSupported(true);
            const recognition = new SpeechRecognitionAPI();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = (event: SpeechRecognitionEvent) => {
                let transcript = '';

                // Collect all results from the current session
                for (let i = 0; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }

                // Always just set the full transcript (not append)
                // This prevents duplication on iOS where interim + final both fire
                setInput(transcript);
                transcriptRef.current = transcript; // Track for auto-submit
            };

            recognition.onerror = (event: any) => {
                // Ignore benign errors like 'no-speech' (silence) or 'aborted' (stopped manually)
                if (event.error === 'no-speech' || event.error === 'aborted' || event.error === 'not-allowed') {
                    if (event.error === 'not-allowed') {
                        console.warn("Microphone access denied");
                    }
                    setIsListening(false);
                    return;
                }
                console.error('Speech recognition error:', event.error);
                setIsListening(false);
            };

            recognition.onend = () => {
                setIsListening(false);
                // Auto-submit if there's content
                if (transcriptRef.current.trim()) {
                    // Small delay to ensure state is updated
                    setTimeout(() => {
                        const form = document.querySelector('form');
                        if (form) {
                            form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                        }
                    }, 100);
                }
            };

            recognitionRef.current = recognition;
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.abort();
            }
        };
    }, []);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [chatHistory, isChatSending]);

    // Cleanup audio on unmount
    useEffect(() => {
        return () => {
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current = null;
            }
        };
    }, []);

    const handleSend = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim() || isChatSending) return;

        // Stop listening if currently active
        if (isListening && recognitionRef.current) {
            recognitionRef.current.stop();
        }

        // Detect if this send was triggered by voice (transcriptRef populated)
        // or effectively by checking if transcript was used recently
        if (transcriptRef.current && input.includes(transcriptRef.current)) {
            setShouldAutoPlay(true);
        } else {
            setShouldAutoPlay(false);
        }
        transcriptRef.current = ""; // Clear for next time

        const msg = input;
        setInput("");
        await sendMessage(msg);
    };

    const toggleListening = useCallback(() => {
        if (!recognitionRef.current) return;

        if (isListening) {
            recognitionRef.current.stop();
            setIsListening(false);
        } else {
            // iOS Safari Fix: Warm up speech synthesis on user interaction
            if ('speechSynthesis' in window) {
                const warmup = new SpeechSynthesisUtterance('');
                warmup.volume = 0;
                window.speechSynthesis.speak(warmup);
            }

            try {
                recognitionRef.current.start();
                setIsListening(true);
            } catch (error) {
                console.error('Failed to start speech recognition:', error);
            }
        }
    }, [isListening]);

    const playAudio = useCallback(async (text: string, idx: number) => {
        // Strip emojis for TTS ensuring clean speech
        const cleanText = text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2700}-\u{27BF}\u{1F900}-\u{1F9FF}\u{1F018}-\u{1F0F5}\u{1F200}-\u{1F270}]/gu, '');

        // Stop currently playing audio or speech
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current = null;
        }
        window.speechSynthesis.cancel();

        // If clicking the same one that's playing, just stop
        if (playingIdx === idx) {
            setPlayingIdx(null);
            return;
        }

        setLoadingIdx(idx);

        // Try client-side TTS first
        if ('speechSynthesis' in window) {
            try {
                const utterance = new SpeechSynthesisUtterance(cleanText);

                // Optional: Select a voice (preferably English female/neutral if available)
                // const voices = window.speechSynthesis.getVoices();
                // utterance.voice = voices.find(v => v.lang === 'en-US') || null;

                let hasStarted = false;
                utterance.onstart = () => {
                    hasStarted = true;
                    setLoadingIdx(null);
                    setPlayingIdx(idx);
                };

                utterance.onend = () => {
                    setPlayingIdx(null);
                };

                utterance.onerror = (e) => {
                    console.error("Speech synthesis error:", e);
                    setPlayingIdx(null);
                    setLoadingIdx(null);
                };

                window.speechSynthesis.speak(utterance);

                // iOS Timeout Fix: If it doesn't start in 500ms, assume stuck and fallback
                await new Promise<void>((resolve, reject) => {
                    setTimeout(() => {
                        if (!hasStarted) {
                            window.speechSynthesis.cancel();
                            reject(new Error("iOS TTS stuck in loading"));
                        } else {
                            resolve();
                        }
                    }, 500);
                });

                return; // Successfully started client-side TTS
            } catch (e) {
                console.warn("Client-side TTS failed, falling back to server:", e);
                // Fallthrough to server-side
            }
        }

        // Server-side fallback (Piper TTS)
        try {
            const response = await requestTTS(cleanText);
            if (response.audio_base64) {
                // Create audio from base64
                const audioBlob = Uint8Array.from(atob(response.audio_base64), c => c.charCodeAt(0));
                const blob = new Blob([audioBlob], { type: 'audio/wav' });
                const url = URL.createObjectURL(blob);

                const audio = new Audio(url);
                audioRef.current = audio;

                audio.onended = () => {
                    setPlayingIdx(null);
                    URL.revokeObjectURL(url);
                };

                audio.onerror = () => {
                    setPlayingIdx(null);
                    URL.revokeObjectURL(url);
                };

                setPlayingIdx(idx);
                await audio.play();
            }
        } catch (error) {
            console.error("Audio playback error:", error);
        } finally {
            setLoadingIdx(null);
        }
    }, [playingIdx]);

    // Auto-play effect
    useEffect(() => {
        if (shouldAutoPlay && !isChatSending && chatHistory.length > 0) {
            const lastMsg = chatHistory[chatHistory.length - 1];
            if (lastMsg.role === 'assistant') {
                playAudio(lastMsg.content, chatHistory.length - 1);
                setShouldAutoPlay(false); // Reset
            }
        }
    }, [chatHistory, isChatSending, shouldAutoPlay, playAudio]);

    const stopAudio = useCallback(() => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current = null;
        }
        window.speechSynthesis.cancel();
        setPlayingIdx(null);
    }, []);

    return (
        <div className="flex flex-col flex-1 h-full overflow-hidden">
            <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {chatHistory.map((msg, idx) => {
                    const isUser = msg.role === "user";
                    const isSystem = msg.role === "system";
                    const isPlaying = playingIdx === idx;
                    const isLoading = loadingIdx === idx;

                    if (isSystem) {
                        return (
                            <div key={idx} className="flex justify-center my-2">
                                <span className="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded-full">{msg.content}</span>
                            </div>
                        );
                    }

                    return (
                        <div key={idx} className={cn("flex gap-3", isUser ? "flex-row-reverse" : "flex-row")}>
                            <div className={cn("w-8 h-8 rounded-full flex items-center justify-center shrink-0", isUser ? "bg-slate-200 text-slate-700" : "bg-primary text-white")}>
                                {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                            </div>
                            <div className={cn("p-3 rounded-2xl max-w-[85%] text-sm",
                                isUser ? "bg-slate-100 text-slate-800 rounded-tr-none" : "bg-white border border-slate-200 shadow-sm text-slate-800 rounded-tl-none")}>
                                {isUser ? (
                                    msg.content
                                ) : (
                                    <>
                                        <div className="prose prose-sm prose-slate max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0">
                                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                {msg.content}
                                            </ReactMarkdown>
                                        </div>
                                        {/* Speaker button for AI messages */}
                                        <div className="mt-2 pt-2 border-t border-slate-100 flex items-center gap-2">
                                            <button
                                                onClick={() => isPlaying ? stopAudio() : playAudio(msg.content, idx)}
                                                disabled={isLoading}
                                                className={cn(
                                                    "flex items-center gap-1.5 text-xs px-2 py-1 rounded-full transition-all",
                                                    isPlaying
                                                        ? "bg-primary/10 text-primary"
                                                        : "text-slate-500 hover:text-primary hover:bg-slate-100"
                                                )}
                                                title={isPlaying ? "Stop audio" : "Play audio"}
                                            >
                                                {isLoading ? (
                                                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                                ) : isPlaying ? (
                                                    <VolumeX className="w-3.5 h-3.5" />
                                                ) : (
                                                    <Volume2 className="w-3.5 h-3.5" />
                                                )}
                                                <span>{isLoading ? "Loading..." : isPlaying ? "Stop" : "Listen"}</span>
                                            </button>
                                        </div>
                                    </>
                                )}
                            </div>
                        </div>
                    );
                })}
                {isChatSending && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center shrink-0 animate-pulse">
                            <Sparkles className="w-4 h-4" />
                        </div>
                        <div className="bg-white border p-3 rounded-2xl rounded-tl-none text-sm text-slate-400">
                            Thinking...
                        </div>
                    </div>
                )}
            </div>

            <form onSubmit={handleSend} className="p-4 border-t bg-white">
                <div className="relative flex items-center gap-2">
                    {/* Microphone button - only show if supported */}
                    {speechSupported && (
                        <button
                            type="button"
                            onClick={toggleListening}
                            disabled={isChatSending}
                            className={cn(
                                "p-2.5 rounded-full transition-all shrink-0",
                                isListening
                                    ? "bg-red-500 text-white animate-pulse"
                                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                            )}
                            title={isListening ? "Stop listening" : "Start voice input"}
                        >
                            {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                        </button>
                    )}

                    <div className="relative flex-1">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={isListening ? "Listening..." : "Ask me anything..."}
                            className={cn(
                                "w-full pl-4 pr-12 py-3 border-transparent focus:bg-white focus:border-primary focus:ring-1 focus:ring-primary rounded-full outline-none transition-all",
                                isListening ? "bg-red-50 border-red-200" : "bg-slate-100"
                            )}
                            disabled={isChatSending}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isChatSending}
                            className="absolute right-2 top-2 p-1.5 bg-primary text-white rounded-full disabled:opacity-50 disabled:bg-slate-300 transition-colors"
                        >
                            <Send className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                {/* Voice input hint */}
                {speechSupported && (
                    <p className="text-xs text-slate-400 mt-2 text-center">
                        {isListening ? "🎤 Speak now..." : "Tap the microphone to use voice input"}
                    </p>
                )}
            </form>
        </div>
    );
}
