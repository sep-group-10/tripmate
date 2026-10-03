import '../../../data/models/trip.dart';

// Ported from web/src/utils/tripFilters.js.

/// Segmented-control labels, in display order.
const tripFilters = ['All', 'Drafts', 'Generated', 'Saved'];

const tripSortLabels = {
  'Recent': 'Recently edited',
  'Name': 'Trip name',
  'Longest': 'Longest trip',
};

const _filterStatus = {
  'All': null,
  'Drafts': TripStatus.draft,
  'Generated': TripStatus.generated,
  'Saved': TripStatus.saved,
};

class GroupedTrips {
  const GroupedTrips(this.saved, this.generated, this.drafts);

  final List<Trip> saved;
  final List<Trip> generated;
  final List<Trip> drafts;

  int get shownCount => saved.length + generated.length + drafts.length;
}

bool _matches(Trip trip, String query) {
  if (query.isEmpty) return true;
  final haystack = [
    trip.title,
    trip.where,
    trip.prompt,
    trip.stage,
  ].whereType<String>().join(' ').toLowerCase();
  return haystack.contains(query);
}

/// Splits trips into the three page sections for one filter and sort.
/// [query] must already be trimmed and lower-case.
GroupedTrips groupTrips(
  List<Trip> trips, {
  String filter = 'All',
  String query = '',
  String sort = 'Recent',
}) {
  final status = _filterStatus[filter];
  List<Trip> pick(TripStatus wanted) {
    if (status != null && status != wanted) return [];
    final matching = trips
        .where((t) => t.status == wanted && _matches(t, query))
        .toList();
    switch (sort) {
      case 'Name':
        matching.sort((a, b) => a.title.compareTo(b.title));
      case 'Longest':
        matching.sort((a, b) => b.dayCount.compareTo(a.dayCount));
    }
    return matching;
  }

  return GroupedTrips(
    pick(TripStatus.saved),
    pick(TripStatus.generated),
    pick(TripStatus.draft),
  );
}
