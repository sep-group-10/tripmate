import 'itinerary_day.dart';

/// DRAFT -> GENERATED -> SAVED (web/src/constants/tripStatus.js).
enum TripStatus { draft, generated, saved }

class Trip {
  const Trip({
    required this.id,
    required this.status,
    required this.title,
    required this.where,
    required this.edited,
    required this.dayCount,
    required this.startDate,
    required this.endDate,
    this.travellers,
    this.budgetLkr = 0,
    this.stage,
    this.progressPercent,
    this.prompt,
    this.coverImageUrl,
    this.days = const [],
  });

  final String id;
  final TripStatus status;
  final String title;

  /// Destinations, e.g. "Kandy · Nuwara Eliya · Ella".
  final String where;

  /// Relative last-edit text, e.g. "2 hours ago".
  final String edited;
  final int dayCount;
  final DateTime startDate;
  final DateTime endDate;
  final int? travellers;
  final int budgetLkr;

  /// Drafts only: planning stage and progress.
  final String? stage;
  final int? progressPercent;
  final String? prompt;
  final String? coverImageUrl;
  final List<ItineraryDay> days;

  Trip copyWith({TripStatus? status, String? title}) => Trip(
    id: id,
    status: status ?? this.status,
    title: title ?? this.title,
    where: where,
    edited: edited,
    dayCount: dayCount,
    startDate: startDate,
    endDate: endDate,
    travellers: travellers,
    budgetLkr: budgetLkr,
    stage: stage,
    progressPercent: progressPercent,
    prompt: prompt,
    coverImageUrl: coverImageUrl,
    days: days,
  );
}
