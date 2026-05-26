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
    if (markers.length > 0) {
      const bounds = new maplibregl.LngLatBounds();
      markers.forEach(marker => {
        if (marker.lat && marker.lon) {
          bounds.extend([marker.lon, marker.lat]);
        }
      });

      if (!bounds.isEmpty()) {
        if (markers.length === 1) {
          map.current.flyTo({
            center: [markers[0].lon, markers[0].lat],
            zoom: 10,
            essential: true
          });
        } else {
          map.current.fitBounds(bounds, { padding: 80, duration: 2000 });
        }
      }
    }

    // Handle geometry (Polyline)
    if (geometry && geometry.length > 0) {
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
        const handleLoad = () => {
          if (!map.current.getSource('route')) {
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
          handleLoad();
        } else {
          map.current.once('load', handleLoad);
        }
      }

      const bounds = new maplibregl.LngLatBounds();
      geometry.forEach(c => bounds.extend([c[1], c[0]]));
      map.current.fitBounds(bounds, { padding: 50 });
    }
  }, [geometry, markers]);

  return <div ref={mapContainer} className="w-full h-full rounded-xl" />;
};

export default Map;
