import React from 'react';

interface TimerRingProps {
  totalSeconds: number;
  remainingSeconds: number;
  label?: string;
  isPaused?: boolean;
}

export const TimerRing: React.FC<TimerRingProps> = ({
  totalSeconds,
  remainingSeconds,
  label = 'Focus Session',
  isPaused = false
}) => {
  const size = 320;
  const strokeWidth = 14;
  const center = size / 2;
  const radius = center - strokeWidth * 2;
  const circumference = 2 * Math.PI * radius;

  const progress = totalSeconds > 0 ? Math.max(0, Math.min(1, remainingSeconds / totalSeconds)) : 1;
  const strokeDashoffset = circumference - progress * circumference;

  const minutes = Math.floor(remainingSeconds / 60);
  const seconds = remainingSeconds % 60;
  const formattedTime = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  return (
    <div className="relative flex flex-col items-center justify-center my-6 select-none">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background Track */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          stroke="#1e293b"
          strokeWidth={strokeWidth}
          fill="transparent"
        />

        {/* Progress Ring with glowing stroke */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          stroke="url(#emeraldGradient)"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-linear"
          style={{
            filter: isPaused
              ? 'none'
              : 'drop-shadow(0 0 12px rgba(34, 197, 94, 0.5))'
          }}
        />

        {/* Gradient Definition */}
        <defs>
          <linearGradient id="emeraldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4ade80" />
            <stop offset="100%" stopColor="#14532d" />
          </linearGradient>
        </defs>
      </svg>

      {/* Inner Time & Label Display */}
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className="text-6xl font-black tracking-tight text-white font-mono drop-shadow-md">
          {formattedTime}
        </span>
        <span className="mt-2 text-sm font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 max-w-[200px] truncate">
          {label}
        </span>
        {isPaused && (
          <span className="mt-2 text-xs font-bold uppercase tracking-widest text-amber-400 animate-pulse">
            PAUSED
          </span>
        )}
      </div>
    </div>
  );
};
