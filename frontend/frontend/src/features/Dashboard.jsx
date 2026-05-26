import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Milestone, 
  Clock, 
  ShieldCheck, 
  ArrowLeft, 
  Map as MapIcon, 
  FileText, 
  LayoutDashboard,
  Settings,
  HelpCircle,
  LogOut,
  Truck,
  History,
  X,
  Menu
} from 'lucide-react';
import { useTrip } from '../hooks/useTrip';
import Map from '../components/Map';
import Timeline from './Timeline';

const Dashboard = () => {
  const { tripData } = useTrip();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  if (!tripData) {
    return (
      <div className="h-screen flex flex-col items-center justify-center bg-surface p-6 text-center">
        <div className="w-20 h-20 bg-secondary/10 text-secondary rounded-full flex items-center justify-center mb-6">
          <Truck className="w-10 h-10" />
        </div>
        <h2 className="text-2xl font-bold text-primary mb-2">No Active Trip Plan</h2>
        <p className="text-on-surface-variant max-w-xs mb-8 text-sm">You haven't generated a trip plan yet. Use our optimization engine to get started.</p>
        <button 
          onClick={() => navigate('/plan')}
          className="px-6 py-3 bg-secondary text-white font-bold rounded-xl shadow-lg hover:shadow-secondary/20 transition-all flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" /> Go to Planner
        </button>
      </div>
    );
  }

  const { summary, timeline, route_stops, route_geometry } = tripData;

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
            <Link to="/dashboard" onClick={() => setIsSidebarOpen(false)} className="flex items-center gap-3 px-4 py-3 bg-white/10 rounded-lg text-sm font-semibold transition-all">
              <LayoutDashboard className="w-4 h-4" /> Dashboard
            </Link>
            <Link to="/plan" onClick={() => setIsSidebarOpen(false)} className="flex items-center gap-3 px-4 py-3 text-on-primary-container hover:bg-white/5 rounded-lg text-sm font-semibold transition-all">
              <MapIcon className="w-4 h-4" /> New Plan
            </Link>
            <Link to="/logs" onClick={() => setIsSidebarOpen(false)} className="flex items-center gap-3 px-4 py-3 text-on-primary-container hover:bg-white/5 rounded-lg text-sm font-semibold transition-all">
              <FileText className="w-4 h-4" /> ELD Logs
            </Link>
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-grow flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b border-outline-variant bg-white flex items-center justify-between px-4 md:px-8 shrink-0">
          <div className="flex items-center gap-4 min-w-0">
            <button onClick={() => setIsSidebarOpen(true)} className="md:hidden p-2 hover:bg-surface-container-low rounded-lg shrink-0">
               <Menu className="w-6 h-6 text-primary" />
            </button>
            <h1 className="text-lg md:text-xl font-bold text-primary truncate">Active Trip Plan</h1>
            <div className="hidden sm:block h-6 w-px bg-outline-variant" />
            <div className="hidden sm:flex items-center gap-2 text-xs font-bold text-on-surface-variant uppercase tracking-wider">
               <Truck className="w-3.5 h-3.5" /> TRUCK-7742
            </div>
          </div>
          <div className="flex items-center gap-4 shrink-0">
            <button 
              onClick={() => navigate('/logs')}
              className="flex items-center gap-2 px-3 md:px-4 py-2 bg-secondary text-white rounded-lg text-[10px] md:text-xs font-bold hover:shadow-lg transition-all"
            >
              <FileText className="w-3.5 h-3.5" /> <span className="hidden sm:inline">View ELD Logs</span>
            </button>
          </div>
        </header>

        <main className="flex-grow overflow-y-auto p-4 md:p-8 flex flex-col gap-6 md:gap-8 custom-scrollbar">
          {/* Metrics - Grid stacks on mobile */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
            <div className="bg-white border border-outline-variant rounded-2xl p-4 md:p-6 shadow-sm flex items-center gap-3 md:gap-4">
              <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-secondary/10 flex items-center justify-center text-secondary shrink-0">
                <MapIcon className="w-5 h-5 md:w-6 md:h-6" />
              </div>
              <div className="min-w-0">
                <p className="text-[8px] md:text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-0.5 truncate">Total Distance</p>
                <p className="text-base md:text-xl font-bold text-primary truncate">{summary.total_distance_miles.toFixed(0)} mi</p>
              </div>
            </div>
            <div className="bg-white border border-outline-variant rounded-2xl p-4 md:p-6 shadow-sm flex items-center gap-3 md:gap-4">
              <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-secondary/10 flex items-center justify-center text-secondary shrink-0">
                <Clock className="w-5 h-5 md:w-6 md:h-6" />
              </div>
              <div className="min-w-0">
                <p className="text-[8px] md:text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-0.5 truncate">Driving Time</p>
                <p className="text-base md:text-xl font-bold text-primary truncate">{summary.total_driving_hours.toFixed(1)}h</p>
              </div>
            </div>
            <div className="bg-white border border-outline-variant rounded-2xl p-4 md:p-6 shadow-sm flex items-center gap-3 md:gap-4">
              <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-teal-500/10 flex items-center justify-center text-teal-600 shrink-0">
                <History className="w-5 h-5 md:w-6 md:h-6" />
              </div>
              <div className="min-w-0">
                <p className="text-[8px] md:text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-0.5 truncate">Total Duration</p>
                <p className="text-base md:text-xl font-bold text-primary truncate">{summary.total_duration_hours.toFixed(1)}h</p>
              </div>
            </div>
            <div className="bg-white border border-outline-variant rounded-2xl p-4 md:p-6 shadow-sm flex items-center gap-3 md:gap-4">
              <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-green-500/10 flex items-center justify-center text-green-600 shrink-0">
                <ShieldCheck className="w-5 h-5 md:w-6 md:h-6" />
              </div>
              <div className="min-w-0">
                <p className="text-[8px] md:text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-0.5 truncate">HOS Status</p>
                <p className="text-base md:text-xl font-bold text-primary truncate">DOT Ready</p>
              </div>
            </div>
          </div>

          <div className="flex-grow flex flex-col lg:flex-row gap-6 md:gap-8">
            {/* Map Container */}
            <div className="flex-[2] relative rounded-2xl border border-outline-variant overflow-hidden shadow-md min-h-[300px] md:min-h-[500px]">
              <Map geometry={route_geometry} markers={route_stops} />
            </div>

            {/* Timeline Sidebar - Stacks below on mobile */}
            <div className="flex-1 bg-white border border-outline-variant rounded-2xl shadow-sm flex flex-col overflow-hidden max-h-[600px] lg:max-h-none shrink-0">
               <div className="p-4 md:p-6 border-b border-outline-variant flex justify-between items-center bg-surface-container-low">
                  <h3 className="font-bold text-primary text-sm md:text-base">Trip Timeline</h3>
                  <span className="text-[10px] font-bold bg-secondary/10 text-secondary px-2 py-1 rounded-full uppercase tracking-tighter shrink-0">
                    {summary.estimated_days} Days
                  </span>
               </div>
               <div className="flex-grow overflow-y-auto p-4 md:p-6 custom-scrollbar">
                  <Timeline events={timeline} />
               </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
