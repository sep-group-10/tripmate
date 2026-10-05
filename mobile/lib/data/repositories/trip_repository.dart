import '../models/trip.dart';

abstract class TripRepository {
  Future<List<Trip>> getTrips();

  /// Throws [RepositoryException] when the trip does not exist.
  Future<Trip> getTrip(String id);

  /// GENERATED -> SAVED.
  Future<Trip> saveTrip(String id);

  /// SAVED -> GENERATED.
  Future<Trip> unsaveTrip(String id);

  Future<Trip> renameDraft(String id, String title);

  Future<void> discardDraft(String id);
}
