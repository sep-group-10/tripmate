class Restaurant {
  const Restaurant({
    required this.id,
    required this.destinationId,
    required this.name,
    required this.cuisine,
    required this.rating,
    required this.priceLevel,
    required this.latitude,
    required this.longitude,
    this.imageUrl,
  });

  final String id;
  final String destinationId;
  final String name;
  final String cuisine;
  final double rating;

  /// 1 (budget) to 3 (fine dining).
  final int priceLevel;
  final double latitude;
  final double longitude;
  final String? imageUrl;
}
