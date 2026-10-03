import 'package:flutter/foundation.dart' show Factory;
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

import '../../../../core/theme/app_colors.dart';
import 'marker_icons.dart';
import 'trip_map_model.dart';

/// Google Map of the plan's stops (web/src/components/chat/TripMap.jsx):
/// numbered pins in each day's color, a line joining each day's stops in visit
/// order, and the camera fitted to whatever is visible. Tapping a pin shows the
/// place name and time. With no stops it shows Sri Lanka.
class TripMap extends StatefulWidget {
  const TripMap({super.key, required this.stops});

  /// The stops to draw (already filtered to the visible days).
  final List<MapStop> stops;

  @override
  State<TripMap> createState() => _TripMapState();
}

class _TripMapState extends State<TripMap> {
  GoogleMapController? _controller;
  final Map<(int, int), BitmapDescriptor> _icons = {};

  @override
  void initState() {
    super.initState();
    _loadIcons();
  }

  @override
  void didUpdateWidget(TripMap old) {
    super.didUpdateWidget(old);
    if (stopsSignature(old.stops) != stopsSignature(widget.stops)) {
      _loadIcons();
      _fit();
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  Future<void> _loadIcons() async {
    for (final stop in widget.stops) {
      final key = (stop.color.toARGB32(), stop.number);
      if (_icons.containsKey(key)) continue;
      final icon = await MarkerIcons.numbered(stop.color, stop.number);
      if (!mounted) return;
      setState(() => _icons[key] = icon);
    }
  }

  Future<void> _fit() async {
    final controller = _controller;
    if (controller == null) return;
    final bounds = boundsOf(widget.stops);
    try {
      if (bounds == null) {
        await controller.animateCamera(
          CameraUpdate.newLatLngZoom(sriLankaCenter, sriLankaZoom),
        );
      } else if (widget.stops.length == 1 ||
          (bounds.northeast.latitude - bounds.southwest.latitude).abs() <
                  1e-5 &&
              (bounds.northeast.longitude - bounds.southwest.longitude).abs() <
                  1e-5) {
        await controller.animateCamera(
          CameraUpdate.newLatLngZoom(bounds.southwest, singleStopZoom),
        );
      } else {
        await controller.animateCamera(
          CameraUpdate.newLatLngBounds(
            LatLngBounds(
              southwest: bounds.southwest,
              northeast: bounds.northeast,
            ),
            fitPadding,
          ),
        );
      }
    } catch (_) {
      // The map may not have a size yet; the next change re-fits.
    }
  }

  @override
  Widget build(BuildContext context) {
    final markers = <Marker>{
      for (final stop in widget.stops)
        Marker(
          markerId: MarkerId('${stop.dayNumber}-${stop.number}-${stop.name}'),
          position: stop.position,
          // Only the day and stop number are needed to stay unique; the
          // callout carries the name and time.
          infoWindow: InfoWindow(title: stop.name, snippet: stop.subtitle),
          icon:
              _icons[(stop.color.toARGB32(), stop.number)] ??
              BitmapDescriptor.defaultMarker,
          anchor: const Offset(0.5, 1),
        ),
    };
    final polylines = <Polyline>{
      for (final entry in routesByDay(widget.stops).entries)
        Polyline(
          polylineId: PolylineId('day-${entry.key}'),
          points: [for (final s in entry.value) s.position],
          color: entry.value.first.color.withValues(alpha: 0.85),
          width: 4,
          startCap: Cap.roundCap,
          endCap: Cap.roundCap,
          jointType: JointType.round,
        ),
    };
    final first = widget.stops.isEmpty ? null : widget.stops.first.position;

    return Container(
      height: 256,
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(AppRadii.panel),
        border: Border.all(color: AppColors.border),
      ),
      child: GoogleMap(
        initialCameraPosition: CameraPosition(
          target: first ?? sriLankaCenter,
          zoom: first == null ? sriLankaZoom : 10,
        ),
        style: mapStyleJson,
        markers: markers,
        polylines: polylines,
        onMapCreated: (controller) {
          _controller = controller;
          WidgetsBinding.instance.addPostFrameCallback((_) => _fit());
        },
        // Pan and zoom with one finger even inside the scrolling tab panel.
        gestureRecognizers: {
          Factory<OneSequenceGestureRecognizer>(EagerGestureRecognizer.new),
        },
        zoomControlsEnabled: false,
        mapToolbarEnabled: false,
        myLocationButtonEnabled: false,
        compassEnabled: false,
        rotateGesturesEnabled: false,
        tiltGesturesEnabled: false,
        buildingsEnabled: false,
        indoorViewEnabled: false,
        trafficEnabled: false,
      ),
    );
  }
}
