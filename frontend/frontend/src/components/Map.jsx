import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const MAPTILER_KEY = import.meta.env.VITE_MAPTILER_API_KEY || 'pgXaE6t0zOSGnqcbTZiY';

const Map = ({ center = [-98.5795, 39.8283], zoom = 3, geometry, markers = [] }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    if (map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: `https://api.maptiler.com/maps/streets-v2/style.json?key=${MAPTILER_KEY}`,
      center: center,
      zoom: zoom,
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
  }, [center, zoom]);

  useEffect(() => {
    if (!map.current) return;

    // Clear existing markers
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    // Add new markers
    markers.forEach(marker => {
      const el = document.createElement('div');
      el.className = 'marker';
      
      let color = '#3b82f6';
      if (marker.type === 'origin') color = '#6b7280';
      if (marker.type === 'pickup') color = '#10b981';
      if (marker.type === 'dropoff') color = '#ef4444';
      if (marker.type === 'fuel') color = '#f59e0b';
      
      const m = new maplibregl.Marker({ color })
        .setLngLat([marker.lon, marker.lat])
        .setPopup(new maplibregl.Popup({ offset: 25 }).setHTML(`<h3>${marker.label}</h3>`))
        .addTo(map.current);
      
      markersRef.current.push(m);
    });

    // Handle markers and camera movement
    const fitMap = () => {
      if (!map.current) return;
      
      const bounds = new maplibregl.LngLatBounds();
      let hasData = false;

      if (markers.length > 0) {
        markers.forEach(marker => {
          if (marker.lat && marker.lon) {
            bounds.extend([marker.lon, marker.lat]);
            hasData = true;
          }
        });
      }

      if (geometry && geometry.length > 0) {
        geometry.forEach(c => {
          bounds.extend([c[1], c[0]]);
          hasData = true;
        });
      }

      if (hasData) {
        map.current.fitBounds(bounds, { 
          padding: { top: 50, bottom: 50, left: 50, right: 50 }, 
          duration: 1000,
          essential: true
        });
        
        // Secondary check to ensure it fits after container might have resized
        setTimeout(() => {
          if (map.current) map.current.resize();
        }, 500);
      }
    };

    if (map.current.loaded()) {
      fitMap();
    } else {
      map.current.once('load', fitMap);
    }

    // Handle geometry layer updates
    if (geometry && geometry.length > 0) {
      const updateSource = () => {
        const source = map.current.getSource('route');
        if (source) {
          source.setData({
            type: 'Feature',
            properties: {},
            geometry: {
              type: 'LineString',
              coordinates: geometry.map(c => [c[1], c[0]]),
            },
          });
        } else {
          map.current.addSource('route', {
            type: 'geojson',
            data: {
              type: 'Feature',
              properties: {},
              geometry: {
                type: 'LineString',
                coordinates: geometry.map(c => [c[1], c[0]]),
              },
            },
          });

          map.current.addLayer({
            id: 'route',
            type: 'line',
            source: 'route',
            layout: { 'line-join': 'round', 'line-cap': 'round' },
            paint: {
              'line-color': '#0058be',
              'line-width': 5,
              'line-opacity': 0.75,
            },
          });
        }
      };

      if (map.current.loaded()) {
        updateSource();
      } else {
        map.current.once('load', updateSource);
      }
    }
  }, [geometry, markers]);

  return <div ref={mapContainer} className="w-full h-full rounded-xl" />;
};

export default Map;
