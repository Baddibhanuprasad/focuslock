import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Zap } from 'lucide-react';
import { alarmAudio } from '../services/audio';

interface DrowsinessOverlayProps {
  isOpen: boolean;
  onDismiss: () => void;
}

export const DrowsinessOverlay: React.FC<DrowsinessOverlayProps> = ({ isOpen, onDismiss }) => {
  const [challengeType, setChallengeType] = useState<'MATH' | 'TYPING'>('MATH');
  
  // Math Challenge State
  const [num1, setNum1] = useState(12);
  const [num2, setNum2] = useState(25);
  const [userMathAnswer, setUserMathAnswer] = useState('');
  
  // Typing Challenge State
  const targetTypingText = "I am awake and ready to study";
  const [userTypingInput, setUserTypingInput] = useState('');
  
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (isOpen) {
      // Start escalating audio alarm sound
      alarmAudio.startEscalatingAlarm();
      
      // Randomize math numbers
      const n1 = Math.floor(Math.random() * 30) + 10;
      const n2 = Math.floor(Math.random() * 40) + 15;
      setNum1(n1);
      setNum2(n2);
      setUserMathAnswer('');
      setUserTypingInput('');
      setErrorMsg('');

      // Random challenge type
      setChallengeType(Math.random() > 0.5 ? 'MATH' : 'TYPING');
    } else {
      alarmAudio.stopAlarm();
    }

    return () => {
      alarmAudio.stopAlarm();
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const handleVerifyMath = (e: React.FormEvent) => {
    e.preventDefault();
    const expected = num1 + num2;
    if (parseInt(userMathAnswer.trim(), 10) === expected) {
      alarmAudio.stopAlarm();
      onDismiss();
    } else {
      setErrorMsg(`Incorrect answer. (${num1} + ${num2} ≠ ${userMathAnswer})`);
    }
  };

  const handleVerifyTyping = (e: React.FormEvent) => {
    e.preventDefault();
    if (userTypingInput.trim() === targetTypingText) {
      alarmAudio.stopAlarm();
      onDismiss();
    } else {
      setErrorMsg('Text does not match. Please re-type carefully.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-xl flex items-center justify-center p-6 animate-fade-in">
      <div className="bg-slate-900 border border-amber-500/40 rounded-3xl p-8 max-w-lg w-full shadow-2xl shadow-amber-500/20 text-center relative overflow-hidden">
        {/* Glowing Alert Header */}
        <div className="w-16 h-16 rounded-2xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center mx-auto mb-4 animate-bounce">
          <AlertTriangle className="w-10 h-10 text-amber-400" />
        </div>

        <h2 className="text-3xl font-extrabold text-white tracking-tight">Drowsiness Alert!</h2>
        <p className="text-slate-300 text-sm mt-2">
          Prolonged eye closure detected. Complete this wake-up challenge to dismiss the alarm!
        </p>

        {errorMsg && (
          <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-xs font-semibold">
            {errorMsg}
          </div>
        )}

        {/* Challenge Section */}
        <div className="mt-6 bg-slate-950/80 p-6 rounded-2xl border border-slate-800 text-left">
          {challengeType === 'MATH' ? (
            <form onSubmit={handleVerifyMath} className="space-y-4">
              <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs uppercase tracking-wider">
                <Zap className="w-4 h-4" /> Math Challenge
              </div>
              <p className="text-xl font-bold text-white font-mono">
                Solve: <span className="text-emerald-400">{num1} + {num2}</span> = ?
              </p>
              <input
                type="number"
                value={userMathAnswer}
                onChange={(e) => setUserMathAnswer(e.target.value)}
                placeholder="Enter answer"
                autoFocus
                className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white font-mono text-lg focus:outline-none focus:border-amber-400"
              />
              <button
                type="submit"
                className="w-full py-3 bg-gradient-to-r from-amber-500 to-emerald-500 text-slate-950 font-bold rounded-xl shadow-lg hover:brightness-110 transition-all flex items-center justify-center gap-2"
              >
                <CheckCircle className="w-5 h-5" /> Submit & Dismiss Alarm
              </button>
            </form>
          ) : (
            <form onSubmit={handleVerifyTyping} className="space-y-4">
              <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs uppercase tracking-wider">
                <Zap className="w-4 h-4" /> Typing Challenge
              </div>
              <p className="text-sm font-semibold text-slate-300">
                Type this phrase exactly:
              </p>
              <div className="p-3 bg-slate-900 rounded-xl border border-slate-700 font-mono text-amber-300 text-sm select-none">
                "{targetTypingText}"
              </div>
              <input
                type="text"
                value={userTypingInput}
                onChange={(e) => setUserTypingInput(e.target.value)}
                placeholder="Type phrase here"
                autoFocus
                className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white font-mono text-sm focus:outline-none focus:border-amber-400"
              />
              <button
                type="submit"
                className="w-full py-3 bg-gradient-to-r from-amber-500 to-emerald-500 text-slate-950 font-bold rounded-xl shadow-lg hover:brightness-110 transition-all flex items-center justify-center gap-2"
              >
                <CheckCircle className="w-5 h-5" /> Submit & Dismiss Alarm
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
