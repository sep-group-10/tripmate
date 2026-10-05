class Destination {
  const Destination({
    required this.id,
    required this.name,
    required this.region,
    required this.tagline,
    required this.description,
    required this.rating,
    required this.bestSeason,
    required this.latitude,
    required this.longitude,
    this.tags = const [],
    this.imageUrl,
  });

  final String id;
  final String name;
  final String region;
  final String tagline;
  final String description;
  final double rating;
  final String bestSeason;
  final double latitude;
  final double longitude;
  final List<String> tags;
  final String? imageUrl;
}
