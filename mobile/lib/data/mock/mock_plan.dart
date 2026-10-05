import '../models/itinerary_day.dart';
import '../models/itinerary_item.dart';
import '../models/trip_plan.dart';

/// The sample plan from web/src/data/tripPlanDummyData.js (TRIP_DUMMY and
/// DEMO_ITINERARY).
ItineraryItem _stop(
  String id,
  ItineraryItemType type,
  String name,
  String start,
  String end,
  double lat,
  double lng,
) => ItineraryItem(
  id: id,
  type: type,
  title: name,
  startTime: start,
  endTime: end,
  latitude: lat,
  longitude: lng,
);

const _attraction = ItineraryItemType.attraction;
const _restaurant = ItineraryItemType.restaurant;

final mockPlan = TripPlan(
  days: [
    ItineraryDay(
      dayNumber: 1,
      date: DateTime(2026, 9, 12),
      dayType: 'arrival',
      distanceKm: 3.2,
      items: [
        _stop(
          'a1',
          _attraction,
          'Temple of the Sacred Tooth Relic',
          '17:30',
          '19:00',
          7.2936,
          80.6413,
        ),
        _stop(
          'r1',
          _restaurant,
          'Dinner at The Kandy House',
          '20:00',
          '22:00',
          7.2906,
          80.6337,
        ),
      ],
    ),
    ItineraryDay(
      dayNumber: 2,
      date: DateTime(2026, 9, 13),
      dayType: 'full',
      distanceKm: 5.8,
      items: [
        _stop(
          'a2',
          _attraction,
          'Royal Botanical Gardens, Peradeniya',
          '09:00',
          '12:00',
          7.2697,
          80.5966,
        ),
        _stop(
          'r2',
          _restaurant,
          'Lunch at The Empire Cafe',
          '13:00',
          '15:30',
          7.2928,
          80.6415,
        ),
      ],
    ),
    ItineraryDay(
      dayNumber: 3,
      date: DateTime(2026, 9, 14),
      dayType: 'full',
      distanceKm: 7.4,
      items: [
        _stop(
          'a3',
          _attraction,
          'Nine Arch Bridge at dawn',
          '06:15',
          '07:30',
          6.8768,
          81.0608,
        ),
        _stop(
          'a4',
          _attraction,
          'Pedro Tea Estate tasting',
          '16:00',
          '17:30',
          6.9765,
          80.7545,
        ),
      ],
    ),
    ItineraryDay(
      dayNumber: 4,
      date: DateTime(2026, 9, 15),
      dayType: 'full',
      distanceKm: 4.1,
      items: [
        _stop(
          'a5',
          _attraction,
          'Little Adam\'s Peak',
          '08:00',
          '11:00',
          6.8667,
          81.0466,
        ),
        _stop(
          'r3',
          _restaurant,
          'Tea-estate lunch above Ella',
          '13:00',
          '14:30',
          6.879,
          81.05,
        ),
      ],
    ),
    ItineraryDay(
      dayNumber: 5,
      date: DateTime(2026, 9, 16),
      dayType: 'full',
      distanceKm: 9.6,
      items: [
        _stop(
          'a6',
          _attraction,
          'Sigiriya Rock Fortress',
          '06:00',
          '09:30',
          7.957,
          80.7603,
        ),
        _stop(
          'a7',
          _attraction,
          'Minneriya elephant safari',
          '15:00',
          '18:00',
          8.0357,
          80.8993,
        ),
      ],
    ),
    ItineraryDay(
      dayNumber: 6,
      date: DateTime(2026, 9, 17),
      dayType: 'full',
      distanceKm: 2.0,
      items: [
        _stop(
          'a8',
          _attraction,
          'World\'s End and Baker\'s Falls',
          '05:30',
          '10:00',
          6.8014,
          80.8008,
        ),
      ],
    ),
    ItineraryDay(
      dayNumber: 7,
      date: DateTime(2026, 9, 18),
      dayType: 'departure',
      distanceKm: 1.2,
      items: [
        _stop(
          'a9',
          _attraction,
          'Kandy market, gifts',
          '10:00',
          '12:00',
          7.2927,
          80.635,
        ),
      ],
    ),
  ],
  summary: TripSummary(
    routeLabel: 'Kandy · Nuwara Eliya · Ella',
    title: 'Seven days through the hill country',
    occasion: '5th anniversary',
    startDate: DateTime(2026, 9, 12),
    endDate: DateTime(2026, 9, 18),
    stopCount: 12,
    travellers: 2,
    pace: 'Relaxed',
    optimisedFor: 'Your itinerary balances the landmarks with quieter neighbourhood hours — the Nine Arch Bridge at dawn before the crowds, and Sigiriya on Day 5 so the climb lands on the coolest morning of the week. Accommodation is anchored at 98 Acres so walks stay short on Days 2 and 3, and spend peaks on Day 1 with the Kandy House dinner.',
    tradeoffs: const [
      Tradeoff(
        TradeoffType.swapped,
        'Horton Plains moved to Day 6 — the Day 4 forecast showed cloud cover before 09:00, which would have hidden World\'s End.',
      ),
      Tradeoff(
        TradeoffType.kept,
        'The Kandy House stayed despite the price: it\'s the only stay within walking distance of the Temple ceremony.',
      ),
      Tradeoff(
        TradeoffType.dropped,
        'Adam\'s Peak — the climb needs a 02:00 start and doesn\'t fit a relaxed pace with two travellers.',
      ),
    ],
  ),
  budget: const TripBudget(
    total: 310400,
    perDay: 44340,
    categories: [
      BudgetCategory('accommodation', 'Accommodation', 148000),
      BudgetCategory('dining', 'Dining', 74400),
      BudgetCategory('transport', 'Transport & driver', 46600),
      BudgetCategory('attractions', 'Attractions', 27900),
      BudgetCategory('misc', 'Market & misc', 13500),
    ],
  ),
);
