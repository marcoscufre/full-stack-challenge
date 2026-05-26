import React from 'react';
import { format } from 'date-fns';
import { 
  Navigation, 
  MapPin, 
  Flag, 
  Fuel, 
  Coffee, 
  Moon, 
  Truck,
  AlertCircle
} from 'lucide-react';

const Timeline = ({ events }) => {
  const getIcon = (type) => {
    switch (type) {
      case 'driving': return <Truck className="w-4 h-4" />;
      case 'on_duty': return <Navigation className="w-4 h-4" />;
      case 'off_duty': return <Coffee className="w-4 h-4" />;
      case 'sleeper': return <Moon className="w-4 h-4" />;
      case 'fuel': return <Fuel className="w-4 h-4" />;
      default: return <Navigation className="w-4 h-4" />;
    }
  };

  const getStatusColor = (type) => {
    switch (type) {
      case 'driving': return 'bg-secondary text-white';
      case 'on_duty': return 'bg-amber-500 text-white';
      case 'off_duty': return 'bg-slate-400 text-white';
      case 'sleeper': return 'bg-teal-500 text-white';
      default: return 'bg-slate-200 text-slate-600';
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {events.map((event, index) => (
        <div key={index} className="flex gap-4 relative">
          {index !== events.length - 1 && (
            <div className="absolute left-[18px] top-8 bottom-0 w-px bg-outline-variant" />
          )}
          
          <div className={`w-9 h-9 rounded-full shrink-0 flex items-center justify-center z-10 ${getStatusColor(event.type)}`}>
            {getIcon(event.type)}
          </div>
          
          <div className="flex-grow pb-6">
            <div className="flex justify-between items-start mb-1">
              <h4 className="text-sm font-bold text-primary">{event.label}</h4>
              <span className="text-xs font-mono font-bold text-on-surface-variant">
                {format(new Date(event.start_at), 'HH:mm')} - {format(new Date(event.end_at), 'HH:mm')}
              </span>
            </div>
            <p className="text-xs text-on-surface-variant flex items-center gap-1 mb-2">
              <MapPin className="w-3 h-3" /> {event.location}
            </p>
            {event.notes && (
              <div className="p-2 bg-surface-container-low rounded-lg border border-outline-variant/30 text-[11px] text-on-surface-variant italic">
                {event.notes}
              </div>
            )}
            <div className="mt-2 text-[10px] font-bold text-outline uppercase tracking-wider">
              Duration: {event.duration_minutes} min
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Timeline;
