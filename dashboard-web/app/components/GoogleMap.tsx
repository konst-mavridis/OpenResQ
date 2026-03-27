"use client";

import { useEffect, useRef } from "react";
import { useLoadScript } from "@react-google-maps/api";
import { MarkerClusterer } from "@googlemaps/markerclusterer";

interface Report {
  id: string;
  latitude: number;
  longitude: number;
  title?: string;
}

interface ReportsGoogleMapProps {
  reports: Report[];
  heatmap?: boolean;
}

export default function ReportsGoogleMap({ reports, heatmap = false }: ReportsGoogleMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!,
    libraries: ["marker", "visualization"],
  });

  useEffect(() => {
    if (!isLoaded || !mapRef.current || !reports.length) return;

    // Center map on first report
    const center = {
      lat: reports[0].latitude,
      lng: reports[0].longitude,
    };

      const map = new google.maps.Map(mapRef.current, {
      zoom: 12,
      center,
      mapTypeId: "satellite",
    });

    if (heatmap) {
      const points = reports.map((r) => new google.maps.LatLng(r.latitude, r.longitude));
      const heatmapLayer = new google.maps.visualization.HeatmapLayer({
        data: points,
        map,
        radius: 30,
        opacity: 0.7,
        gradient: [
          "rgba(0, 0, 0, 0)",
          "rgba(255, 0, 0, 0.6)",
          "rgba(255, 165, 0, 0.7)",
          "rgba(255, 255, 0, 0.8)",
          "rgba(0, 255, 0, 0.9)",
        ],
      });

      return () => {
        heatmapLayer.setMap(null);
      };
    }

    const infoWindow = new google.maps.InfoWindow({
      content: "",
      disableAutoPan: true,
    });

    const markers = reports.map((r) => {
      const marker = new google.maps.marker.AdvancedMarkerElement({
        position: { lat: r.latitude, lng: r.longitude },
        map,
        title: r.title || "Incident",
      });

      marker.addListener("click", () => {
        infoWindow.setContent(
          `<div class="font-semibold text-gray-900">${r.title || "Incident"}</div><div class="text-gray-400">${r.latitude}, ${r.longitude}</div>`
        );
        infoWindow.open(map, marker);
      });

      return marker;
    });

    const clusterer = new MarkerClusterer({ markers, map });

    return () => {
      markers.forEach((marker) => {
        marker.map = null;
      });
      clusterer.clearMarkers();
    };
  }, [isLoaded, reports, heatmap]);

  if (loadError) return <div>Error loading map</div>;
  if (!isLoaded) return <div>Loading map…</div>;

  return <div ref={mapRef} className="w-full h-full rounded-lg" />;
}
