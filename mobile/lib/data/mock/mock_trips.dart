import '../models/itinerary_day.dart';
import '../models/itinerary_item.dart';
import '../models/trip.dart';
import '../models/user.dart';

/// Sample account and trips, taken from web/src/data/myTripsDummyData.js.
abstract final class MockAccount {
  static const user = User(
    id: 'u1',
    name: 'Nimali Perera',
    email: 'nimali@example.com',
    budgetStyle: 'Moderate',
    pace: 'Balanced',
    interests: ['Culture', 'Food'],
  );

  /// Password of the sample account.
  static const password = 'password123';
}

ItineraryDay _day(
  int number,
  DateTime start,
  String stops, {
  ItineraryItemType type = ItineraryItemType.attraction,
}) {
  final titles = stops.split(' · ');
  return ItineraryDay(
    dayNumber: number,
    date: start.add(Duration(days: number - 1)),
    items: [
      for (var i = 0; i < titles.length; i++)
        ItineraryItem(id: 'd$number-$i', type: type, title: titles[i]),
    ],
  );
}

Trip _planned({
  required String id,
  required TripStatus status,
  required String title,
  required String where,
  required int dayCount,
  required int travellers,
  required int budget,
  required String edited,
  required DateTime start,
  required List<String> plan,
}) => Trip(
  id: id,
  status: status,
  title: title,
  where: where,
  edited: edited,
  dayCount: dayCount,
  startDate: start,
  endDate: start.add(Duration(days: dayCount - 1)),
  travellers: travellers,
  budgetLkr: budget,
  days: [for (var i = 0; i < plan.length; i++) _day(i + 1, start, plan[i])],
);

final mockTrips = <Trip>[
  _planned(
    id: 'saved-1',
    status: TripStatus.saved,
    title: '4 days in Kandy and Ella',
    where: 'Kandy · Nuwara Eliya · Ella',
    dayCount: 4,
    travellers: 2,
    budget: 240000,
    edited: 'last week',
    start: DateTime(2026, 11, 6),
    plan: [
      'Temple of the Sacred Tooth Relic · Kandy Lake · Dinner',
      'Royal Botanical Gardens · Scenic drive to Nuwara Eliya',
      'Nine Arch Bridge at dawn · Little Adam\'s Peak',
    ],
  ),
  _planned(
    id: 'saved-2',
    status: TripStatus.saved,
    title: '6 days of beaches and culture',
    where: 'Negombo · Galle · Unawatuna',
    dayCount: 6,
    travellers: 4,
    budget: 380000,
    edited: '2 weeks ago',
    start: DateTime(2026, 12, 20),
    plan: [
      'Negombo fish market · Lagoon sunset',
      'Galle Fort walk · Dutch Reformed Church',
    ],
  ),
  _planned(
    id: 'generated-1',
    status: TripStatus.generated,
    title: '7 days in the Cultural Triangle',
    where: 'Sigiriya · Polonnaruwa · Kandy',
    dayCount: 7,
    travellers: 2,
    budget: 310000,
    edited: 'yesterday',
    start: DateTime(2026, 9, 12),
    plan: [
      'Sigiriya Rock Fortress · Water gardens · Hotel Sigiriya',
      'Pidurangala sunrise · Minneriya safari · Village lunch',
      'Polonnaruwa ruins · Gal Vihara · Cycle the sacred quadrangle',
    ],
  ),
  _planned(
    id: 'generated-2',
    status: TripStatus.generated,
    title: '5 days on the south coast',
    where: 'Galle · Mirissa · Tangalle',
    dayCount: 5,
    travellers: 2,
    budget: 195000,
    edited: '4 days ago',
    start: DateTime(2026, 10, 24),
    plan: [
      'Galle Fort ramparts · Sea Spray dinner · Amangalla',
      'Mirissa whale watching · Coconut Tree Hill sunset',
    ],
  ),
  Trip(
    id: 'draft-1',
    status: TripStatus.draft,
    title: 'Untitled trip',
    where: 'Destination not set',
    edited: '2 hours ago',
    stage: 'Collecting preferences',
    progressPercent: 18,
    prompt: '“I want a 6-day trip under LKR 120,000. We prefer beaches and cultural sites rather than city crowds…”',
    dayCount: 6,
    startDate: DateTime(2026, 11, 1),
    endDate: DateTime(2026, 11, 6),
  ),
  Trip(
    id: 'draft-2',
    status: TripStatus.draft,
    title: 'Hill country loop',
    where: 'Nuwara Eliya · Kandy · Ella',
    edited: 'yesterday',
    stage: 'Choosing hotels',
    progressPercent: 62,
    prompt: '“Ten days across the hill country, mixing Nuwara Eliya and Kandy. Budget around LKR 250,000 for two people…”',
    dayCount: 10,
    startDate: DateTime(2026, 12, 1),
    endDate: DateTime(2026, 12, 10),
  ),
  Trip(
    id: 'draft-3',
    status: TripStatus.draft,
    title: 'Sri Lanka adventure',
    where: 'Yala · Mirissa · Galle',
    edited: '3 days ago',
    stage: 'Budget optimisation',
    progressPercent: 84,
    prompt: '“Family trip with two kids, we want to see elephants and beaches. Eight days total, flexible on timing…”',
    dayCount: 8,
    startDate: DateTime(2027, 1, 5),
    endDate: DateTime(2027, 1, 12),
  ),
];
