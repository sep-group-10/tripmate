import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:mobile/core/maps/maps_availability.dart';
import 'package:mobile/core/theme/app_colors.dart';
import 'package:mobile/core/theme/app_theme.dart';
import 'package:mobile/data/models/itinerary_day.dart';
import 'package:mobile/data/models/itinerary_item.dart';
import 'package:mobile/features/chat/presentation/widgets/map_tab.dart';
import 'package:mobile/features/chat/presentation/widgets/trip_map_model.dart';

ItineraryItem _item(String id, String name, double? lat, double? lng) =>
    ItineraryItem(
      id: id,
      type: ItineraryItemType.attraction,
      title: name,
      startTime: '09:00',
      endTime: '10:30',
      latitude: lat,
      longitude: lng,
    );

final _days = [
  ItineraryDay(
    dayNumber: 1,
    date: DateTime(2026, 11, 10),
    items: [
      _item('a', 'Temple', 7.29, 80.64),
      _item('b', 'No coordinates', null, null),
      _item('c', 'Lake', 7.30, 80.65),
    ],
  ),
  ItineraryDay(
    dayNumber: 2,
    date: DateTime(2026, 11, 11),
    items: [_item('d', 'Gardens', 7.27, 80.60)],
  ),
];

void main() {
  group('trip map model', () {
    test('keeps only stops with coordinates, numbered like the Itinerary tab', () {
      final stops = mapStops(_days);
      expect(stops.map((s) => s.name), ['Temple', 'Lake', 'Gardens']);
      // "Lake" is the 3rd item of day 1 even though item 2 has no coordinates.
      expect(stops.map((s) => s.number), [1, 3, 1]);
      expect(stops.map((s) => s.dayNumber), [1, 1, 2]);
    });

    test('day colors follow the web palette and wrap around', () {
      expect(dayColor(0), AppColors.accent);
      expect(dayColor(1), AppColors.info);
      expect(dayColor(4), AppColors.warn);
      expect(dayColor(5), AppColors.accent);
    });

    test('marker callout shows the day and the time', () {
      expect(mapStops(_days).first.subtitle, 'Day 1 · 09:00–10:30');
    });

    test('filtering by day keeps that day\'s stops and visit order', () {
      final stops = mapStops(_days);
      expect(visibleStops(stops, {2}).map((s) => s.name), ['Gardens']);
      expect(visibleStops(stops, {1, 2}), hasLength(3));
      expect(visibleStops(stops, {}), isEmpty);
    });

    test(
      'routes join each day\'s stops in order; one-stop days have no line',
      () {
        final routes = routesByDay(mapStops(_days));
        expect(routes.keys, [1]);
        expect(routes[1]!.map((s) => s.name), ['Temple', 'Lake']);
      },
    );

    test('bounds cover the visible stops; none means the island view', () {
      final bounds = boundsOf(mapStops(_days))!;
      expect(bounds.southwest, const LatLng(7.27, 80.60));
      expect(bounds.northeast, const LatLng(7.30, 80.65));
      expect(boundsOf(const []), isNull);
    });

    test('signature changes only when the visible pins change', () {
      final stops = mapStops(_days);
      expect(stopsSignature(stops), stopsSignature(mapStops(_days)));
      expect(
        stopsSignature(stops),
        isNot(stopsSignature(visibleStops(stops, {2}))),
      );
    });

    test('the map style is set in code and uses no cloud Map ID', () {
      expect(mapStyleJson, contains('"featureType"'));
    });
  });

  group('MapTab without a Maps key', () {
    setUp(MapsAvailability.resetForTest);

    testWidgets('shows the day chips and legs list, and no map', (
      tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.light(useWebFonts: false),
          home: Scaffold(
            body: SingleChildScrollView(child: MapTab(days: _days)),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(GoogleMap), findsNothing);
      expect(find.textContaining('Day 1 · Nov 10'), findsOneWidget);
      expect(find.textContaining('Day 2 · Nov 11'), findsOneWidget);
      expect(find.text('LEG 1'), findsOneWidget);
      expect(find.textContaining('Temple → Lake'), findsOneWidget);
      expect(find.textContaining('Straight-line distances'), findsOneWidget);
    });
  });
}
