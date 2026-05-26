import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Calendar, 
  ChevronLeft, 
  ChevronRight, 
  FileText, 
  LayoutDashboard, 
  Map as MapIcon, 
  Truck,
  History,
  HelpCircle,
  LogOut,
  Download,
  Menu,
  X
} from 'lucide-react';
import { useTrip } from '../hooks/useTrip';
import EldGrid from '../components/EldGrid';
import { format } from 'date-fns';

const EldLogsPage = () => {
  const { tripData } = useTrip();
  const navigate = useNavigate();
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  if (!tripData) {
    return (
      <div className="h-screen flex flex-col items-center justify-center bg-surface p-6 text-center">
        <div className="w-20 h-20 bg-secondary/10 text-secondary rounded-full flex items-center justify-center mb-6">
          <FileText className="w-10 h-10" />
        </div>
        <h2 className="text-2xl font-bold text-primary mb-2">No Active Logs</h2>
        <p className="text-on-surface-variant max-w-xs mb-8 text-sm">Generate a trip plan first to view Electronic Logging Device data.</p>
        <button 
          onClick={() => navigate('/plan')}
          className="px-6 py-3 bg-secondary text-white font-bold rounded-xl shadow-lg hover:shadow-secondary/20 transition-all flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" /> Go to Planner
        </button>
      </div>
    );
  }

  const { daily_logs } = tripData;
  const selectedLog = daily_logs[selectedDayIndex];

  return (
    <div className="flex h-screen bg-surface overflow-hidden relative">
      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-primary/20 backdrop-blur-sm z-[60] md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar - Responsive */}
      <aside className={`fixed inset-y-0 left-0 w-64 bg-primary-container text-white flex flex-col shrink-0 z-[70] transition-transform duration-300 md:relative md:translate-x-0 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="p-6 h-full flex flex-col">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-secondary rounded-lg flex items-center justify-center">
                <Truck className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-lg tracking-tight">Mission Control</span>
            </div>
            <button onClick={() => setIsSidebarOpen(false)} className="md:hidden">
              <X className="w-6 h-6 text-white" />
            </button>
          </div>
          
          <nav className="space-y-1">
            <Link to="/dashboard" onClick={() => setIsSidebarOpen(false)} className="flex items-center gap-3 px-4 py-3 text-on-primary-container hover:bg-white/5 rounded-lg text-sm font-semibold transition-all">
              <LayoutDashboard className="w-4 h-4" /> Dashboard
            </Link>
            <Link to="/plan" onClick={() => setIsSidebarOpen(false)} className="flex items-center gap-3 px-4 py-3 text-on-primary-container hover:bg-white/5 rounded-lg text-sm font-semibold transition-all">
              <MapIcon className="w-4 h-4" /> New Plan
            </Link>
            <Link to="/logs" onClick={() => setIsSidebarOpen(false)} className="flex items-center gap-3 px-4 py-3 bg-white/10 rounded-lg text-sm font-semibold transition-all">
              <FileText className="w-4 h-4" /> ELD Logs
            </Link>
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-grow flex flex-col min-w-0 overflow-hidden">
        <header className="h-16 border-b border-outline-variant bg-white flex items-center justify-between px-4 md:px-8 shrink-0">
          <div className="flex items-center gap-4 min-w-0">
            <button onClick={() => setIsSidebarOpen(true)} className="md:hidden p-2 hover:bg-surface-container-low rounded-lg shrink-0">
               <Menu className="w-6 h-6 text-primary" />
            </button>
            <h1 className="text-lg md:text-xl font-bold text-primary truncate">Daily ELD Logs</h1>
          </div>
        </header>

        <main className="flex-grow overflow-y-auto p-4 md:p-8 flex flex-col gap-6 md:gap-8 custom-scrollbar">
          {/* Date Selector */}
          <div className="flex justify-between items-center bg-white p-3 md:p-4 rounded-xl border border-outline-variant shadow-sm shrink-0">
            <button 
              onClick={() => setSelectedDayIndex(Math.max(0, selectedDayIndex - 1))}
              disabled={selectedDayIndex === 0}
              className="p-1.5 md:p-2 hover:bg-surface-container-low rounded-lg disabled:opacity-30 transition-all shrink-0"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            
            <div className="text-center min-w-0 px-2">
              <p className="text-[8px] md:text-[10px] font-bold text-outline uppercase tracking-widest truncate">Day {selectedLog.day_index} of {daily_logs.length}</p>
              <h2 className="text-sm md:text-lg font-bold text-primary truncate">{format(new Date(selectedLog.date_label), 'EEEE, MMM dd, yyyy')}</h2>
            </div>

            <button 
              onClick={() => setSelectedDayIndex(Math.min(daily_logs.length - 1, selectedDayIndex + 1))}
              disabled={selectedDayIndex === daily_logs.length - 1}
              className="p-1.5 md:p-2 hover:bg-surface-container-low rounded-lg disabled:opacity-30 transition-all shrink-0"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          {/* Recaps - Grid stacks on mobile */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4 shrink-0">
             <div className="bg-white border border-outline-variant rounded-xl p-3 md:p-4">
                <p className="text-[8px] md:text-[10px] font-bold text-on-surface-variant uppercase mb-1">Driving</p>
                <p className="text-base md:text-lg font-bold text-primary">{selectedLog.recap.driving_hours.toFixed(1)}h</p>
             </div>
             <div className="bg-white border border-outline-variant rounded-xl p-3 md:p-4">
                <p className="text-[8px] md:text-[10px] font-bold text-on-surface-variant uppercase mb-1">On Duty (ND)</p>
                <p className="text-base md:text-lg font-bold text-primary">{selectedLog.recap.on_duty_not_driving_hours.toFixed(1)}h</p>
             </div>
             <div className="bg-white border border-outline-variant rounded-xl p-3 md:p-4">
                <p className="text-[8px] md:text-[10px] font-bold text-on-surface-variant uppercase mb-1">Off Duty</p>
                <p className="text-base md:text-lg font-bold text-primary">{selectedLog.recap.off_duty_hours.toFixed(1)}h</p>
             </div>
             <div className="bg-white border border-outline-variant rounded-xl p-3 md:p-4">
                <p className="text-[8px] md:text-[10px] font-bold text-on-surface-variant uppercase mb-1">Sleeper</p>
                <p className="text-base md:text-lg font-bold text-primary">{selectedLog.recap.sleeper_hours.toFixed(1)}h</p>
             </div>
          </div>

          {/* The Grid */}
          <div className="space-y-4 shrink-0">
             <h3 className="font-bold text-primary text-sm md:text-base flex items-center gap-2">
                <FileText className="w-4 h-4 text-secondary" /> 24-Hour Duty Status Grid
             </h3>
             <EldGrid grid={selectedLog.grid} />
          </div>

          {/* Remarks */}
          <div className="bg-surface-container-low p-5 md:p-6 rounded-xl border border-outline-variant/50 shrink-0">
             <h4 className="text-[10px] md:text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-4">Daily Remarks</h4>
             <ul className="space-y-2">
                {selectedLog.remarks.map((remark, i) => (
                  <li key={i} className="text-xs md:text-sm text-primary flex gap-3">
                    <span className="text-outline font-mono text-xs mt-0.5 shrink-0">•</span>
                    <span className="break-words">{remark}</span>
                  </li>
                ))}
             </ul>
          </div>
        </main>
      </div>
    </div>
  );
};

export default EldLogsPage;
