import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../data/models/itinerary_day.dart';

/// Day colors from web/src/components/chat/MapTab.jsx (DAY_COLORS), reused when
/// there are more days than colors.
const dayColors = [
  AppColors.accent,
  AppColors.info,
  AppColors.muted500,
  AppColors.success,
  AppColors.warn,
];

Color dayColor(int dayIndex) => dayColors[dayIndex % dayColors.length];

/// One stop with valid coordinates, ready to draw.
class MapStop {
  const MapStop({
    required this.dayNumber,
    required this.dayIndex,
    required this.number,
    required this.name,
    required this.position,
    this.startTime,
    this.endTime,
  });

  final int dayNumber;

  /// Position of the day in the plan; picks the color.
  final int dayIndex;

  /// Position of the stop in its day, counting stops that have no coordinates
  /// too, so pins match the numbering on the Itinerary tab.
  final int number;
  final String name;
  final LatLng position;
  final String? startTime;
  final String? endTime;

  Color get color => dayColor(dayIndex);

  /// "Day 2 · 09:00–11:00", the text under the name in the marker's callout.
  String get subtitle {
    final times = startTime == null
        ? ''
        : ' · $startTime${endTime == null ? '' : '–$endTime'}';
    return 'Day $dayNumber$times';
  }
}

/// Every stop of [days] that has coordinates, in visit order.
List<MapStop> mapStops(List<ItineraryDay> days) => [
  for (var d = 0; d < days.length; d++)
    for (var i = 0; i < days[d].items.length; i++)
      if (days[d].items[i].hasCoordinates)
        MapStop(
          dayNumber: days[d].dayNumber,
          dayIndex: d,
          number: i + 1,
          name: days[d].items[i].title,
          position: LatLng(
            days[d].items[i].latitude!,
            days[d].items[i].longitude!,
          ),
          startTime: days[d].items[i].startTime,
          endTime: days[d].items[i].endTime,
        ),
];

/// The stops of the days in [visibleDays] (day numbers).
List<MapStop> visibleStops(List<MapStop> stops, Set<int> visibleDays) => [
  for (final s in stops)
    if (visibleDays.contains(s.dayNumber)) s,
];

/// One line per visible day, joining that day's stops in visit order. Days
/// with fewer than two stops have no line.
Map<int, List<MapStop>> routesByDay(List<MapStop> stops) {
  final byDay = <int, List<MapStop>>{};
  for (final s in stops) {
    byDay.putIfAbsent(s.dayNumber, () => []).add(s);
  }
  byDay.removeWhere((_, list) => list.length < 2);
  return byDay;
}

/// Changes only when the set of visible pins changes, so a rebuild with the
/// same stops does not re-fit the camera and undo the user's panning.
String stopsSignature(List<MapStop> stops) => stops
    .map((s) => '${s.position.latitude},${s.position.longitude}')
    .join('|');

/// The camera target for [stops]: null when there are none (show the island).
({LatLng southwest, LatLng northeast})? boundsOf(List<MapStop> stops) {
  if (stops.isEmpty) return null;
  var south = stops.first.position.latitude;
  var north = south;
  var west = stops.first.position.longitude;
  var east = west;
  for (final s in stops) {
    final p = s.position;
    if (p.latitude < south) south = p.latitude;
    if (p.latitude > north) north = p.latitude;
    if (p.longitude < west) west = p.longitude;
    if (p.longitude > east) east = p.longitude;
  }
  return (southwest: LatLng(south, west), northeast: LatLng(north, east));
}

/// Same fallback as the web map: the centre of Sri Lanka.
const sriLankaCenter = LatLng(7.8731, 80.7718);
const sriLankaZoom = 7.0;
const singleStopZoom = 13.0;
const fitPadding = 48.0;

/// Light map style set in code only (no cloud Map ID), using the web palette.
const mapStyleJson = '''
[
  {"featureType":"poi.business","stylers":[{"visibility":"off"}]},
  {"featureType":"transit","stylers":[{"visibility":"off"}]},
  {"featureType":"landscape","elementType":"geometry","stylers":[{"color":"#f5f6f6"}]},
  {"featureType":"water","elementType":"geometry","stylers":[{"color":"#d8e4fd"}]}
]
''';
