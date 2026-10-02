import { useEffect, useMemo, useState } from "react";
import {
  APIProvider,
  AdvancedMarker,
  InfoWindow,
  Map,
  Pin,
  useMap,
} from "@vis.gl/react-google-maps";

// Same setup as components/LocationPicker.jsx: the shared key, Google's
// placeholder Map ID (needed for AdvancedMarker) and the beta channel.
const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
const MAP_ID = "DEMO_MAP_ID";

const FALLBACK_CENTER = { lat: 7.8731, lng: 80.7718 }; // Sri Lanka centroid
const FALLBACK_ZOOM = 7;
const SINGLE_STOP_ZOOM = 13;
const FIT_PADDING = 48;

// Fits the camera to every pin whenever the set of pins changes. The pins are
// passed as a string so a re-render with the same stops doesn't re-fit and
// undo the user's panning and zooming.
function FitBounds({ signature }) {
  const map = useMap();
  const points = useMemo(
    () =>
      signature
        ? signature.split("|").map((pair) => {
            const [lat, lng] = pair.split(",").map(Number);
            return { lat, lng };
          })
        : [],
    [signature],
  );

  useEffect(() => {
    if (!map || points.length === 0) return;
    if (points.length === 1) {
      map.setCenter(points[0]);
      map.setZoom(SINGLE_STOP_ZOOM);
      return;
    }
    const lats = points.map((point) => point.lat);
    const lngs = points.map((point) => point.lng);
    map.fitBounds(
      {
        north: Math.max(...lats),
        south: Math.min(...lats),
        east: Math.max(...lngs),
        west: Math.min(...lngs),
      },
      FIT_PADDING,
    );
  }, [map, points]);

  return null;
}

/** Map of the plan's stops. `stops` are `{ key, name, lat, lng, number,
 * day_number, start_time?, pinColor }`; the caller only passes stops that have
 * valid coordinates. With none, the map shows Sri Lanka. */
function TripMap({ stops }) {
  const [selectedKey, setSelectedKey] = useState(null);

  if (!API_KEY) {
    return (
      <p className="m-0 flex h-64 flex-none items-center justify-center rounded-panel bg-danger-100 px-6 text-center text-sm text-danger">
        Map unavailable: VITE_GOOGLE_MAPS_API_KEY is not configured.
      </p>
    );
  }

  const selected = stops.find((stop) => stop.key === selectedKey) ?? null;
  const signature = stops.map((stop) => `${stop.lat},${stop.lng}`).join("|");

  return (
    <div className="h-64 flex-none overflow-hidden rounded-panel border border-border">
      <APIProvider apiKey={API_KEY} version="beta">
        <Map
          mapId={MAP_ID}
          defaultCenter={FALLBACK_CENTER}
          defaultZoom={FALLBACK_ZOOM}
          // Cooperative so scrolling the tab panel over the map doesn't zoom it.
          gestureHandling="cooperative"
          streetViewControl={false}
          mapTypeControl={false}
          onClick={() => setSelectedKey(null)}
        >
          <FitBounds signature={signature} />
          {stops.map((stop) => (
            <AdvancedMarker
              key={stop.key}
              position={{ lat: stop.lat, lng: stop.lng }}
              title={stop.name}
              onClick={() => setSelectedKey(stop.key)}
            >
              <Pin
                background={stop.pinColor}
                borderColor="#ffffff"
                glyphColor="#ffffff"
                glyph={String(stop.number)}
              />
            </AdvancedMarker>
          ))}
          {selected && (
            <InfoWindow
              position={{ lat: selected.lat, lng: selected.lng }}
              pixelOffset={[0, -42]}
              onCloseClick={() => setSelectedKey(null)}
            >
              <div className="font-body text-ink">
                <p className="m-0 text-sm font-semibold">{selected.name}</p>
                <p className="m-0 text-helper text-muted-600">
                  Day {selected.day_number}
                  {selected.start_time ? ` · ${selected.start_time}` : ""}
                </p>
              </div>
            </InfoWindow>
          )}
        </Map>
      </APIProvider>
    </div>
  );
}

export default TripMap;
