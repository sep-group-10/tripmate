import { useEffect, useId, useState } from "react";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  Pin,
  useAdvancedMarkerRef,
} from "@vis.gl/react-google-maps";
import { PlacePicker } from "@googlemaps/extended-component-library/react";

// Follows Google's own gmpx-place-picker + Map/AdvancedMarker reference
// (https://developers.google.com/maps/documentation/javascript/examples/rgm-college-picker):
// gmpx-place-picker (search box, from @googlemaps/extended-component-library)
// drives a @vis.gl/react-google-maps <Map> via its `forMap` attribute, and we
// drop an AdvancedMarker/Pin at the picked place.location ourselves.
const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

// Google's shared placeholder Map ID - lets AdvancedMarker render without
// the project needing its own Cloud Console-configured Map ID/style. Swap
// for a real one if custom map styling is ever wanted.
const MAP_ID = "DEMO_MAP_ID";

const FALLBACK_CENTER = { lat: 7.8731, lng: 80.7718 }; // Sri Lanka centroid
const FALLBACK_ZOOM = 7;
const REGION_ZOOM = 11;
const PICKED_ZOOM = 16;

// Coordinates coming from a Destination (backend/app/schemas/tourism.py's
// Decimal fields, serialized as numeric strings e.g. "7.2906") must be
// coerced to real numbers here - @vis.gl/react-google-maps' isLatLngLiteral
// check requires Number.isFinite(lat/lng) and otherwise crashes trying to
// call .toJSON() on a plain object.
function toLatLng(coords) {
  if (!coords) return null;
  const lat = Number(coords.latitude);
  const lng = Number(coords.longitude);
  return Number.isFinite(lat) && Number.isFinite(lng) ? { lat, lng } : null;
}

function resolveCameraProps(value, initialCenter) {
  const picked = toLatLng(value);
  if (picked) return { center: picked, zoom: PICKED_ZOOM };
  const region = toLatLng(initialCenter);
  if (region) return { center: region, zoom: REGION_ZOOM };
  return { center: FALLBACK_CENTER, zoom: FALLBACK_ZOOM };
}

// AdvancedMarkerElement's post-drag position is a LatLngAltitude-shaped
// object (plain `.lat`/`.lng` number properties), not a classic LatLng (with
// `.lat()`/`.lng()` methods) - handle either, since which one shows up isn't
// pinned down by public docs.
function readLatLng(position) {
  if (!position) return null;
  const lat =
    typeof position.lat === "function" ? position.lat() : position.lat;
  const lng =
    typeof position.lng === "function" ? position.lng() : position.lng;
  return Number.isFinite(lat) && Number.isFinite(lng)
    ? { latitude: lat, longitude: lng }
    : null;
}

function positionKey(value, initialCenter) {
  return [
    value?.latitude,
    value?.longitude,
    initialCenter?.latitude,
    initialCenter?.longitude,
  ].join(",");
}

/** Shared search-box + map + pin location picker for the admin Attraction/
 * Hotel/Restaurant forms (C4's location-picker follow-up) - replaces
 * silently defaulting a new record's coordinates to its destination's.
 * `value` is `{ latitude, longitude } | null`; `onChange` receives the same
 * shape once a real place is picked. `initialCenter` (typically the
 * selected Destination's coordinates) only affects where the map starts
 * before a place is picked - once `value` is set (a fresh pick, or an
 * existing record being edited), the map centers on that instead.
 * Once a pin is showing (from either a search pick or an edited record's
 * saved position), it's always draggable - search results often land near
 * but not exactly on the real spot, so dragging lets the admin nudge it;
 * `onChange` fires again on drop with the marker's new position. */
function LocationPicker({ value, onChange, initialCenter }) {
  const rawId = useId();
  const mapDomId = `location-picker-${rawId.replace(/[^a-zA-Z0-9-]/g, "")}`;

  const [cameraProps, setCameraProps] = useState(() =>
    resolveCameraProps(value, initialCenter),
  );
  // Re-derive the camera whenever the picked location or the destination's
  // coordinates change (a fresh pick, switching destinations, or opening
  // the edit form for a different record) - done during render rather than
  // in an effect, per React's "adjusting state when props change" pattern,
  // since cameraProps must still stay independently controllable by the
  // user panning/zooming the map afterwards (via onCameraChanged below).
  const [syncedKey, setSyncedKey] = useState(() =>
    positionKey(value, initialCenter),
  );
  const currentKey = positionKey(value, initialCenter);
  if (currentKey !== syncedKey) {
    setSyncedKey(currentKey);
    setCameraProps(resolveCameraProps(value, initialCenter));
  }

  const [markerRef, marker] = useAdvancedMarkerRef();

  // AdvancedMarkerElement dispatches its drag-end as a DOM CustomEvent named
  // 'gmp-dragend' (per Google's draggable-markers guide), not the classic
  // 'dragend' google.maps.event that @vis.gl/react-google-maps' onDragEnd
  // prop listens for via google.maps.event.addListener - that prop never
  // fires here, so the native event is bound directly off the marker
  // instance instead. The event carries no position data; read it back off
  // marker.position afterwards, as the guide does.
  useEffect(() => {
    if (!marker) return;
    const handleDragEnd = () => {
      const dragged = readLatLng(marker.position);
      if (dragged) onChange(dragged);
    };
    marker.addEventListener("gmp-dragend", handleDragEnd);
    return () => marker.removeEventListener("gmp-dragend", handleDragEnd);
  }, [marker, onChange]);

  if (!API_KEY) {
    return (
      <p className="m-0 rounded-lg bg-danger-100 px-3 py-2.5 text-sm text-danger">
        Location picker unavailable: VITE_GOOGLE_MAPS_API_KEY is not configured.
      </p>
    );
  }

  const markerPosition = toLatLng(value);

  return (
    <APIProvider apiKey={API_KEY} version="beta">
      <div className="flex flex-col gap-2">
        <PlacePicker
          forMap={mapDomId}
          placeholder="Search for a place…"
          className="w-full"
          onPlaceChange={(event) => {
            const place = event.target.value;
            if (place?.location) {
              onChange({
                latitude: place.location.lat(),
                longitude: place.location.lng(),
              });
            }
          }}
        />
        <div className="h-64 w-full overflow-hidden rounded-lg border border-border">
          <Map
            id={mapDomId}
            mapId={MAP_ID}
            {...cameraProps}
            onCameraChanged={(event) => setCameraProps(event.detail)}
            gestureHandling="greedy"
            disableDefaultUI={false}
          >
            {markerPosition && (
              <AdvancedMarker
                ref={markerRef}
                position={markerPosition}
                draggable
              >
                <Pin
                  background="#FBBC04"
                  glyphColor="#000"
                  borderColor="#000"
                />
              </AdvancedMarker>
            )}
          </Map>
        </div>
      </div>
    </APIProvider>
  );
}

export default LocationPicker;
