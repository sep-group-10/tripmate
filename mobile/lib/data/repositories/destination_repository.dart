import '../models/attraction.dart';
import '../models/destination.dart';
import '../models/hotel.dart';
import '../models/restaurant.dart';

abstract class DestinationRepository {
  Future<List<Destination>> getDestinations();

  /// Case-insensitive match on name, region and tags. Empty query returns all.
  Future<List<Destination>> search(String query);

  Future<Destination?> getDestination(String id);

  Future<List<Attraction>> getAttractions(String destinationId);

  Future<List<Hotel>> getHotels(String destinationId);

  Future<List<Restaurant>> getRestaurants(String destinationId);
}
