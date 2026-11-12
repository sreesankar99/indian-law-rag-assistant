"use client";
import { useState, useEffect, useRef } from "react";

type Section = {
  act: string;
  section_no: string;
  title: string;
  text: string;
};

export default function Home() {
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("en");
  const [answer, setAnswer] = useState("");
  const [sections, setSections] = useState<Section[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  // Voice input state
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Initialize Speech Recognition if available
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;

        recognitionRef.current.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setQuery(transcript);
          setIsListening(false);
        };

        recognitionRef.current.onerror = () => {
          setIsListening(false);
        };
      }
    }
  }, []);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      if (recognitionRef.current) {
        if (language === "hi") recognitionRef.current.lang = "hi-IN";
        else if (language === "ml") recognitionRef.current.lang = "ml-IN";
        else recognitionRef.current.lang = "en-IN";
        recognitionRef.current.start();
        setIsListening(true);
      } else {
        alert("Voice input is not supported in this browser. Please use Chrome or Edge.");
      }
    }
  };

  const handleAsk = async () => {
    if (!query.trim() || loading) return;
    setLoading(true);
    setAnswer("");
    setSections([]);
    setError("");

    try {
      // The backend now handles both direct lookups and AI search in one endpoint
      const res = await fetch("http://localhost:8000/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, language }),
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const data = await res.json();
      setAnswer(data.answer);
      setSections(data.sections_used || []);
    } catch (err: any) {
      setError("Could not reach the backend. Is the FastAPI server running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center pt-8">
          <h1 className="text-4xl font-bold text-blue-900">
            ⚖️ Indian Law Assistant
          </h1>
          <p className="text-gray-600 mt-2">
            Ask about BNS, IPC, or Fundamental Rights in plain language.
          </p>
        </div>

        {/* Disclaimer */}
        <div className="bg-amber-50 border border-amber-200 text-amber-900 text-xs rounded-lg p-3">
          ⚠️ This is an informational tool only. Not legal advice. Consult a
          qualified lawyer for actual legal matters.
        </div>

        {/* Language Selector */}
        <div className="flex justify-end">
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="border p-2 rounded-lg bg-white text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी (Hindi)</option>
            <option value="ml">മലയാളം (Malayalam)</option>

          </select>
        </div>

        {/* Search Box */}
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            placeholder={language === "hi" ? "उदाहरण: चोरी की सजा क्या है?" : language === "ml" ? "ഉദാഹരണത്തിന്: മോഷണത്തിനുള്ള ശിക്ഷ എന്താണ്?" :"e.g. What is the punishment for theft?"}
            className="flex-1 p-3 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          
          {/* Voice Button */}
          <button
            onClick={toggleListening}
            className={`px-4 rounded-lg font-medium shadow-sm transition-colors ${
              isListening ? "bg-red-500 text-white animate-pulse" : "bg-white text-gray-700 border hover:bg-gray-50"
            }`}
            title="Voice Input"
          >
            {isListening ? "⏹ Stop" : "🎤 Speak"}
          </button>

          <button
            onClick={handleAsk}
            disabled={loading || !query.trim()}
            className="bg-blue-900 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-800 disabled:opacity-50 shadow-sm"
          >
            {loading ? "Thinking..." : "Ask"}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-900 p-4 rounded-lg">
            {error}
          </div>
        )}

        {/* AI Answer */}
        {answer && (
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-bold text-lg text-blue-900">
                🤖 Answer
              </h2>
              <button
                onClick={() => {
                  const utterance = new SpeechSynthesisUtterance(answer);
                   if (language === "hi") utterance.lang = "hi-IN";
                  else if (language === "ml") utterance.lang = "ml-IN";
                  else utterance.lang = "en-IN";
                  window.speechSynthesis.speak(utterance);
                }}
                className="bg-gray-100 text-gray-700 px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-gray-200 shadow-sm"
              >
                🔊 Listen
              </button>
            </div>
            <p className="whitespace-pre-wrap text-gray-800 leading-relaxed">
              {answer}
            </p>
          </div>
        )}

        {/* Retrieved Sections */}
        {sections.length > 0 && (
          <div>
            <h2 className="font-bold text-lg mb-3 text-gray-700">
              📜 Retrieved from Database
            </h2>
            <div className="grid gap-3">
              {sections.map((s, i) => (
                <div
                  key={i}
                  className="bg-white p-5 rounded-lg shadow-sm border border-gray-200"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-bold bg-blue-900 text-white px-2 py-0.5 rounded">
                      {s.act} {s.section_no}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    {s.title}
                  </h3>
                  <div className="text-sm text-gray-700 bg-gray-50 p-4 rounded border border-gray-200 max-h-96 overflow-y-auto whitespace-pre-wrap">
                    {s.text}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <footer className="text-center text-xs text-gray-400 pt-8 pb-4">
          Built with Next.js + FastAPI + Gemini RAG · © 2026
        </footer>
      </div>
    </main>
  );
}