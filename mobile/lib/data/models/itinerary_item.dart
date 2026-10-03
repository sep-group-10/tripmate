/// Categories of a stop, as in the web chat itinerary
/// (web/src/components/chat/ItineraryTab.jsx).
enum ItineraryItemType {
  attraction,
  restaurant,
  hotel,
  localEvent,

  /// A category this app does not know; see [ItineraryItem.rawCategory].
  other,
}

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
    this.rawCategory,
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

  /// The backend's category string, kept for [ItineraryItemType.other].
  final String? rawCategory;

  bool get hasCoordinates => latitude != null && longitude != null;
}
