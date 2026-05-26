import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Timer, Route, ShieldCheck, Map as MapIcon, ChevronRight } from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="bg-background min-h-screen">
      {/* Header - Responsive */}
      <header className="h-16 md:h-20 bg-surface/90 docked full-width top-0 sticky backdrop-blur-md border-b border-outline-variant shadow-sm z-40">
        <div className="flex justify-between items-center w-full px-4 md:px-lg h-full max-w-7xl mx-auto">
          <div className="flex items-center gap-md">
            <span className="font-inter text-xl md:text-2xl font-bold text-secondary">ELD Route Planner</span>
          </div>
          <div className="flex items-center gap-4">
             <button onClick={() => navigate('/plan')} className="px-4 md:px-6 py-2 md:py-2.5 bg-secondary text-white rounded-lg font-semibold text-xs md:text-sm hover:bg-secondary-container transition-all shadow-sm">
                Launch App
             </button>
          </div>
        </div>
      </header>

      <main className="overflow-x-hidden">
        {/* Hero Section - Responsive spacing and font sizes */}
        <section className="relative pt-12 md:pt-24 pb-12 md:pb-16 px-6 lg:px-12 max-w-7xl mx-auto flex flex-col items-center text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1 bg-secondary-fixed text-on-secondary-fixed rounded-full mb-6 md:mb-8 border border-secondary/20">
            <ShieldCheck className="w-4 h-4 text-secondary" />
            <span className="text-[10px] md:text-xs font-semibold uppercase tracking-wider">DOT FMCSA Compliant</span>
          </div>
          
          <h1 className="font-inter text-3xl md:text-4xl lg:text-6xl font-bold text-primary mb-4 md:mb-6 max-w-4xl leading-tight">
            Plan Routes and Generate <span className="text-secondary">ELD Logs</span> Automatically
          </h1>
          
          <p className="text-base md:text-lg text-on-surface-variant max-w-2xl mb-8 md:mb-10">
            The high-performance route optimization engine designed specifically for commercial drivers. Eliminate manual log errors, maximize driving hours, and ensure 100% compliance.
          </p>
          
          <div className="flex justify-center w-full mb-20">
            <button 
              onClick={() => navigate('/plan')}
              className="px-8 py-4 bg-secondary text-white font-semibold rounded-xl shadow-lg hover:shadow-secondary/20 hover:-translate-y-0.5 active:translate-y-0 active:scale-95 transition-all flex items-center gap-2 text-lg"
            >
              Start Planning
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>

          {/* Dashboard Preview */}
          <div className="w-full relative group max-w-5xl">
            <div className="absolute -inset-4 bg-gradient-to-tr from-secondary/10 to-transparent blur-3xl opacity-50"></div>
            <div className="relative bg-white rounded-xl border border-outline-variant shadow-2xl overflow-hidden aspect-video flex items-center justify-center bg-slate-50">
               <div className="text-center p-8">
                  <div className="w-16 h-16 bg-secondary/10 text-secondary rounded-full flex items-center justify-center mx-auto mb-4">
                    <MapIcon className="w-8 h-8" />
                  </div>
                  <h3 className="text-xl font-bold text-primary">Interactive Trip Planner</h3>
                  <p className="text-on-surface-variant mt-2">Visualizing HOS-compliant routes with real-time data.</p>
               </div>
            </div>
          </div>
        </section>

        {/* Quick Features */}
        <section className="py-24 px-6 lg:px-12 max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 bg-surface-container-lowest border border-outline-variant rounded-xl">
              <Timer className="w-10 h-10 text-secondary mb-4" />
              <h3 className="text-xl font-bold mb-2">HOS Engine</h3>
              <p className="text-on-surface-variant text-sm">Automated 11/14/70 hour rule enforcement for property-carrying drivers.</p>
            </div>
            <div className="p-8 bg-surface-container-lowest border border-outline-variant rounded-xl">
              <Route className="w-10 h-10 text-secondary mb-4" />
              <h3 className="text-xl font-bold mb-2">Truck Routing</h3>
              <p className="text-on-surface-variant text-sm">Precise directions using OpenRouteService with truck-specific profiles.</p>
            </div>
            <div className="p-8 bg-surface-container-lowest border border-outline-variant rounded-xl">
              <ShieldCheck className="w-10 h-10 text-secondary mb-4" />
              <h3 className="text-xl font-bold mb-2">ELD Logs</h3>
              <p className="text-on-surface-variant text-sm">Downloadable FMCSA-style daily logs generated from your trip plan.</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-outline-variant py-12 bg-surface-container-lowest">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="text-secondary font-bold text-xl">ELD Route Planner</div>
          <div className="text-on-surface-variant text-sm">© 2026 Mission Control Logistics. All rights reserved.</div>
          <div className="flex gap-6 text-sm font-semibold text-on-surface-variant">
            <a href="#" className="hover:text-secondary">Privacy Policy</a>
            <a href="#" className="hover:text-secondary">Terms of Service</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
