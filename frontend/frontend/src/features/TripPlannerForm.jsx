import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { MapPin, Flag, Timer, ArrowRight, Loader2, Navigation, X } from 'lucide-react';
import { useTrip } from '../hooks/useTrip';
import Map from '../components/Map';
import LocationAutocomplete from '../components/LocationAutocomplete';

const TripPlannerForm = () => {
  const { control, handleSubmit, watch, formState: { errors } } = useForm({
    defaultValues: {
      current_location: { display_name: 'Miami, FL', lat: 25.7617, lon: -80.1918 },
      pickup_location: null,
      dropoff_location: null,
      current_cycle_used_hours: 10,
    }
  });
  
  const { planTrip, loading, error } = useTrip();
  const navigate = useNavigate();
  
  const [showNotice, setShowNotice] = useState(true);
  const currentCycleUsed = watch('current_cycle_used_hours');
  const currentLocation = watch('current_location');
  const pickupLocation = watch('pickup_location');
  const dropoffLocation = watch('dropoff_location');

  // Auto-hide notice
  useEffect(() => {
    const timer = setTimeout(() => setShowNotice(false), 5000);
    return () => clearTimeout(timer);
  }, []);

  const onSubmit = async (data) => {
    // Transform data back to strings for the API
    const payload = {
      ...data,
      current_location: data.current_location?.display_name || "",
      pickup_location: data.pickup_location?.display_name || "",
      dropoff_location: data.dropoff_location?.display_name || "",
    };
    try {
      await planTrip(payload);
      navigate('/dashboard');
    } catch (err) {
      console.error(err);
    }
  };

  // Build markers for the map
  const mapMarkers = [
    currentLocation && { ...currentLocation, type: 'origin', label: 'Current' },
    pickupLocation && { ...pickupLocation, type: 'pickup', label: 'Pickup' },
    dropoffLocation && { ...dropoffLocation, type: 'dropoff', label: 'Dropoff' }
  ].filter(Boolean);

  return (
    <div className="flex flex-col h-screen bg-surface overflow-x-hidden md:overflow-hidden">
      {/* Top Nav */}
      <header className="h-16 border-b border-outline-variant bg-white flex items-center justify-between px-4 md:px-6 shrink-0">
        <div className="flex items-center gap-2">
          <span className="font-bold text-secondary text-sm md:text-lg">ELD Route Planner</span>
        </div>
        <div className="flex items-center gap-3 md:gap-6">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 md:w-8 md:h-8 rounded-full bg-secondary text-white flex items-center justify-center text-[10px] md:text-xs font-bold">1</div>
            <span className="hidden md:inline text-xs font-bold text-secondary">Configuration</span>
          </div>
          <div className="w-4 md:w-8 h-px bg-outline-variant" />
          <div className="flex items-center gap-2 opacity-40">
            <div className="w-6 h-6 md:w-8 md:h-8 rounded-full border border-outline flex items-center justify-center text-[10px] md:text-xs font-bold">2</div>
            <span className="hidden md:inline text-xs font-bold">Optimization</span>
          </div>
        </div>
      </header>

      <div className="flex flex-col md:flex-row flex-grow overflow-y-auto md:overflow-hidden">
        {/* Form Sidebar - Stacks on top on mobile */}
        <aside className="w-full md:w-[400px] bg-white border-r border-outline-variant flex flex-col p-6 shrink-0 overflow-y-visible md:overflow-y-auto">
          <header className="mb-8">
            <h1 className="text-xl md:text-2xl font-bold text-primary mb-1">New Trip Planning</h1>
            <p className="text-xs md:text-sm text-on-surface-variant">Configure your route and DOT compliance metrics.</p>
          </header>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 flex-grow flex flex-col">
            <div className="space-y-4">
              <Controller
                name="current_location"
                control={control}
                rules={{ required: "Starting location is required" }}
                render={({ field }) => (
                  <LocationAutocomplete 
                    label="Current Location"
                    icon={Navigation}
                    value={field.value?.display_name}
                    onChange={field.onChange}
                    placeholder="Enter start location"
                    error={errors.current_location?.message}
                  />
                )}
              />

              <Controller
                name="pickup_location"
                control={control}
                rules={{ required: "Pickup point is required" }}
                render={({ field }) => (
                  <LocationAutocomplete 
                    label="Pickup Point"
                    icon={MapPin}
                    value={field.value?.display_name}
                    onChange={field.onChange}
                    placeholder="Enter pickup address"
                    error={errors.pickup_location?.message}
                  />
                )}
              />

              <Controller
                name="dropoff_location"
                control={control}
                rules={{ required: "Dropoff destination is required" }}
                render={({ field }) => (
                  <LocationAutocomplete 
                    label="Dropoff Destination"
                    icon={Flag}
                    value={field.value?.display_name}
                    onChange={field.onChange}
                    placeholder="Enter delivery address"
                    error={errors.dropoff_location?.message}
                  />
                )}
              />
            </div>

            <div className="p-4 bg-surface-container-low rounded-xl border border-outline-variant/50 mt-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-primary flex items-center gap-2">
                  <Timer className="w-4 h-4 text-secondary" /> HOS Context
                </h3>
                <span className="text-xs font-bold text-secondary">Cycle: 70h/8d</span>
              </div>
              <div className="space-y-3">
                <label className="text-sm text-on-surface-variant block font-medium">Current Cycle Hours Used</label>
                <div className="flex items-center gap-4">
                  <Controller
                    name="current_cycle_used_hours"
                    control={control}
                    render={({ field }) => (
                      <input 
                        type="range" 
                        {...field}
                        min="0" max="70" step="0.5"
                        className="flex-grow accent-secondary h-1 bg-surface-container-highest rounded-lg appearance-none cursor-pointer"
                      />
                    )}
                  />
                  <span className="text-xs font-mono font-bold w-12 text-right">{currentCycleUsed}h</span>
                </div>
              </div>
            </div>

            {error && (
              <div className="p-3 bg-error-container text-on-error-container rounded-lg text-xs font-medium border border-error/20 flex gap-2 items-start">
                <Loader2 className="w-3 h-3 text-error rotate-45 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <div className="mt-auto pt-6">
              <button 
                type="submit"
                disabled={loading}
                className="w-full bg-secondary text-white py-4 rounded-xl font-bold text-sm hover:shadow-lg hover:shadow-secondary/20 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                  <>
                    Calculate Optimized Route
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </div>
          </form>
        </aside>

        {/* Map Panel - Ensure min-height on mobile */}
        <main className="flex-grow relative bg-surface-container-low min-h-[400px] md:min-h-0">
          <div className="absolute inset-4 overflow-hidden rounded-2xl shadow-inner border border-outline-variant">
            <Map markers={mapMarkers} />
          </div>
          
          {/* Fading Notice */}
          <div className={`absolute top-8 right-8 p-4 bg-white/90 backdrop-blur-md border border-outline-variant rounded-xl shadow-xl z-10 max-w-xs transition-all duration-1000 ${showNotice ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4 pointer-events-none'}`}>
            <div className="flex justify-between items-start mb-2">
              <h4 className="text-sm font-bold text-primary">Truck Optimization</h4>
              <button onClick={() => setShowNotice(false)} className="text-outline hover:text-primary transition-colors">
                <X className="w-3 h-3" />
              </button>
            </div>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Our engine uses OpenRouteService with a Heavy Vehicle profile to avoid low bridges and weight limits.
            </p>
          </div>
        </main>
      </div>
    </div>
  );
};

export default TripPlannerForm;
