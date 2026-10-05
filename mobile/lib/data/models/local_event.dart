class LocalEvent {
  const LocalEvent({
    required this.id,
    required this.destinationId,
    required this.title,
    required this.description,
    required this.venue,
    required this.startDate,
    required this.endDate,
    this.imageUrl,
  });

  final String id;
  final String destinationId;
  final String title;
  final String description;
  final String venue;
  final DateTime startDate;
  final DateTime endDate;
  final String? imageUrl;
}
