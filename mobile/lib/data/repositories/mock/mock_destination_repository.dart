import '../../mock/mock_data.dart';
import '../../mock/mock_delay.dart';
import '../../models/attraction.dart';
import '../../models/destination.dart';
import '../../models/hotel.dart';
import '../../models/restaurant.dart';
import '../destination_repository.dart';

class MockDestinationRepository implements DestinationRepository {
  @override
  Future<List<Destination>> getDestinations() async {
    await mockDelay();
    return MockData.destinations;
  }

  @override
  Future<List<Destination>> search(String query) async {
    await mockDelay(250);
    final q = query.trim().toLowerCase();
    if (q.isEmpty) return MockData.destinations;
    return MockData.destinations
        .where(
          (d) =>
              d.name.toLowerCase().contains(q) ||
              d.region.toLowerCase().contains(q) ||
              d.tags.any((t) => t.toLowerCase().contains(q)),
        )
        .toList();
  }

  @override
  Future<Destination?> getDestination(String id) async {
    await mockDelay(200);
    for (final d in MockData.destinations) {
      if (d.id == id) return d;
    }
    return null;
  }

  @override
  Future<List<Attraction>> getAttractions(String destinationId) async {
    await mockDelay();
    return MockData.attractions
        .where((a) => a.destinationId == destinationId)
        .toList();
  }

  @override
  Future<List<Hotel>> getHotels(String destinationId) async {
    await mockDelay();
    return MockData.hotels
        .where((h) => h.destinationId == destinationId)
        .toList();
  }

  @override
  Future<List<Restaurant>> getRestaurants(String destinationId) async {
    await mockDelay();
    return MockData.restaurants
        .where((r) => r.destinationId == destinationId)
        .toList();
  }
}
