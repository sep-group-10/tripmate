import 'itinerary_item.dart';

class ItineraryDay {
  const ItineraryDay({
    required this.dayNumber,
    required this.date,
    required this.items,
    this.title,
    this.summary,
    this.dayType,
    this.distanceKm,
  });

  final int dayNumber;
  final DateTime date;
  final List<ItineraryItem> items;
  final String? title;
  final String? summary;

  /// "arrival", "full" or "departure".
  final String? dayType;
  final double? distanceKm;
}
