class Hotel {
  const Hotel({
    required this.id,
    required this.destinationId,
    required this.name,
    required this.stars,
    required this.rating,
    required this.pricePerNightLkr,
    required this.latitude,
    required this.longitude,
    this.amenities = const [],
    this.imageUrl,
  });

  final String id;
  final String destinationId;
  final String name;
  final int stars;
  final double rating;
  final int pricePerNightLkr;
  final double latitude;
  final double longitude;
  final List<String> amenities;
  final String? imageUrl;
}
