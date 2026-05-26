import React, { useState, useEffect, useRef } from 'react';
import { plannerService } from '../services/api';
import { Loader2, Search, MapPin } from 'lucide-react';

const LocationAutocomplete = ({ label, icon: Icon, value, onChange, placeholder, error }) => {
  const [query, setQuery] = useState(value || '');
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const delayDebounceFn = setTimeout(async () => {
      if (query.length > 2 && isOpen) {
        setLoading(true);
        try {
          const data = await plannerService.searchLocations(query);
          setResults(data);
        } catch (err) {
          console.error('Geocoding error:', err);
        } finally {
          setLoading(false);
        }
      } else {
        setResults([]);
      }
    }, 400);

    return () => clearTimeout(delayDebounceFn);
  }, [query, isOpen]);

  const handleSelect = (item) => {
    setQuery(item.display_name);
    onChange(item); // Pass the whole item with lat/lon
    setIsOpen(false);
  };

  return (
    <div className="space-y-1 relative" ref={containerRef}>
      <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">{label}</label>
      <div className="relative">
        <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-outline" />
        <input 
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          className={`w-full pl-10 pr-10 py-3 bg-surface border rounded-lg focus:ring-2 focus:ring-secondary/20 focus:border-secondary outline-none transition-all text-sm ${
            error ? 'border-error' : 'border-outline-variant'
          }`}
          placeholder={placeholder}
        />
        {loading && <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-secondary animate-spin" />}
      </div>

      {isOpen && (results.length > 0 || loading) && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-outline-variant rounded-xl shadow-2xl overflow-hidden max-h-60 overflow-y-auto">
          {loading && results.length === 0 ? (
            <div className="p-4 text-center text-xs text-on-surface-variant italic">Searching...</div>
          ) : (
            results.map((item, index) => (
              <button
                key={index}
                type="button"
                onClick={() => handleSelect(item)}
                className="w-full text-left px-4 py-3 hover:bg-surface-container-low transition-colors border-b border-outline-variant/30 last:border-0 flex gap-3 items-start"
              >
                <MapPin className="w-4 h-4 text-outline shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-primary line-clamp-1">{item.display_name}</p>
                </div>
              </button>
            ))
          )}
        </div>
      )}
      {error && <p className="text-xs text-error mt-1">{error}</p>}
    </div>
  );
};

export default LocationAutocomplete;
