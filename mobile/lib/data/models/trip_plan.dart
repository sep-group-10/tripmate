import 'itinerary_day.dart';

enum TradeoffType { swapped, kept, dropped }

class Tradeoff {
  const Tradeoff(this.type, this.text);

  final TradeoffType type;
  final String text;
}

class TripSummary {
  const TripSummary({
    required this.routeLabel,
    required this.title,
    required this.occasion,
    required this.startDate,
    required this.endDate,
    required this.stopCount,
    required this.travellers,
    required this.pace,
    required this.optimisedFor,
    required this.tradeoffs,
  });

  final String routeLabel;
  final String title;
  final String occasion;
  final DateTime startDate;
  final DateTime endDate;
  final int stopCount;
  final int travellers;
  final String pace;
  final String optimisedFor;
  final List<Tradeoff> tradeoffs;
}

class BudgetCategory {
  const BudgetCategory(this.key, this.label, this.amount);

  /// accommodation, dining, transport, attractions or misc.
  final String key;
  final String label;
  final int amount;
}

class TripBudget {
  const TripBudget({
    required this.total,
    required this.perDay,
    required this.categories,
    this.currency = 'LKR',
  });

  final int total;
  final int perDay;
  final String currency;
  final List<BudgetCategory> categories;
}

/// A stop the planner could not fit in, with its reason.
class UnscheduledItem {
  const UnscheduledItem({required this.name, this.reason});

  final String name;
  final String? reason;
}

/// What the Summary, Map, Itinerary and Budget tabs show once a plan exists.
class TripPlan {
  const TripPlan({
    required this.days,
    required this.summary,
    required this.budget,
    this.unscheduled = const [],
    this.warnings = const [],
  });

  final List<ItineraryDay> days;
  final List<UnscheduledItem> unscheduled;
  final List<String> warnings;
  final TripSummary summary;
  final TripBudget budget;
}
