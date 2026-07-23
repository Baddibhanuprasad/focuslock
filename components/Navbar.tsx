import React from 'react';
import { Shield, BellOff, Camera, Wifi, Clock, History, Settings, BarChart2 } from 'lucide-react';
import { SessionState } from '../../../shared/src/types';

interface NavbarProps {
  currentView: 'home' | 'active' | 'summary' | 'history' | 'settings';
  setCurrentView: (view: 'home' | 'active' | 'summary' | 'history' | 'settings') => void;
  sessionState: SessionState;
  notificationsSuppressed: boolean;
  webcamActive: boolean;
  extensionConnected: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentView,
  setCurrentView,
  sessionState,
  notificationsSuppressed,
  webcamActive,
  extensionConnected
}) => {
  return (
    <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 px-6 py-4 flex items-center justify-between sticky top-0 z-40">
      {/* Brand */}
      <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentView(sessionState === 'ACTIVE' ? 'active' : 'home')}>
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
          <Shield className="w-6 h-6 text-slate-950 stroke-[2.5]" />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            FocusLock <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">v1.0</span>
          </h1>
          <p className="text-xs text-slate-400 font-medium">Desktop Focus & Screen Monitor</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="flex items-center gap-1 bg-slate-950/60 p-1.5 rounded-2xl border border-slate-800/80">
        <button
          onClick={() => setCurrentView(sessionState === 'ACTIVE' ? 'active' : 'home')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            currentView === 'home' || currentView === 'active'
              ? 'bg-emerald-500 text-slate-950 font-semibold shadow-md shadow-emerald-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <Clock className="w-4 h-4" />
          {sessionState === 'ACTIVE' ? 'Active Session' : 'Timer'}
        </button>

        <button
          onClick={() => setCurrentView('summary')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            currentView === 'summary'
              ? 'bg-emerald-500 text-slate-950 font-semibold shadow-md shadow-emerald-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <BarChart2 className="w-4 h-4" />
          Analytics
        </button>

        <button
          onClick={() => setCurrentView('history')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            currentView === 'history'
              ? 'bg-emerald-500 text-slate-950 font-semibold shadow-md shadow-emerald-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <History className="w-4 h-4" />
          History
        </button>

        <button
          onClick={() => setCurrentView('settings')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            currentView === 'settings'
              ? 'bg-emerald-500 text-slate-950 font-semibold shadow-md shadow-emerald-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <Settings className="w-4 h-4" />
          Settings
        </button>
      </nav>

      {/* System Status Indicators */}
      <div className="flex items-center gap-3">
        {/* Notifications badge */}
        <div
          title={notificationsSuppressed ? 'OS Notifications Suppressed' : 'OS Notifications Normal'}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border ${
            notificationsSuppressed
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
              : 'bg-slate-800/50 border-slate-700 text-slate-400'
          }`}
        >
          <BellOff className="w-3.5 h-3.5" />
          <span>{notificationsSuppressed ? 'Quiet Mode' : 'Quiet Off'}</span>
        </div>

        {/* Webcam badge */}
        <div
          title={webcamActive ? 'Webcam Monitoring Active' : 'Webcam Disabled'}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border ${
            webcamActive
              ? 'bg-teal-500/10 border-teal-500/30 text-teal-400'
              : 'bg-slate-800/50 border-slate-700 text-slate-400'
          }`}
        >
          <Camera className="w-3.5 h-3.5" />
          <span>{webcamActive ? 'Cam Active' : 'Cam Off'}</span>
        </div>

        {/* Extension websocket status badge */}
        <div
          title={extensionConnected ? 'Companion Chrome Extension Connected' : 'Extension Disconnected'}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border ${
            extensionConnected
              ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400'
              : 'bg-slate-800/50 border-slate-700 text-slate-400'
          }`}
        >
          <Wifi className="w-3.5 h-3.5" />
          <span>{extensionConnected ? 'Ext Ready' : 'No Ext'}</span>
        </div>
      </div>
    </header>
  );
};
