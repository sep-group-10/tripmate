class Attraction {
  const Attraction({
    required this.id,
    required this.destinationId,
    required this.name,
    required this.category,
    required this.description,
    required this.rating,
    required this.durationMinutes,
    required this.entryFeeLkr,
    required this.latitude,
    required this.longitude,
    this.imageUrl,
  });

  final String id;
  final String destinationId;
  final String name;
  final String category;
  final String description;
  final double rating;
  final int durationMinutes;

  /// 0 means free entry.
  final int entryFeeLkr;
  final double latitude;
  final double longitude;
  final String? imageUrl;
}
