/// Categories of a stop, as in the web chat itinerary
/// (web/src/components/chat/ItineraryTab.jsx).
enum ItineraryItemType { attraction, restaurant, hotel, localEvent }

class ItineraryItem {
  const ItineraryItem({
    required this.id,
    required this.type,
    required this.title,
    this.startTime,
    this.endTime,
    this.description = '',
    this.location,
    this.latitude,
    this.longitude,
  });

  final String id;
  final ItineraryItemType type;
  final String title;

  /// 24h "HH:mm".
  final String? startTime;
  final String? endTime;
  final String description;
  final String? location;
  final double? latitude;
  final double? longitude;

  bool get hasCoordinates => latitude != null && longitude != null;
}
