import '../models/local_event.dart';

abstract class EventRepository {
  /// Events ordered by start date, optionally limited to one destination.
  Future<List<LocalEvent>> getEvents({String? destinationId});
}
