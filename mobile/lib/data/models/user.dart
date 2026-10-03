/// Fields follow the web profile (web/src/pages/ProfilePage.jsx).
class User {
  const User({
    required this.id,
    required this.name,
    required this.email,
    this.budgetStyle = 'Moderate',
    this.pace = 'Balanced',
    this.interests = const [],
    this.avatarUrl,
  });

  final String id;
  final String name;
  final String email;

  /// One of Budget, Moderate, Luxury.
  final String budgetStyle;

  /// One of Relaxed, Balanced, Packed.
  final String pace;
  final List<String> interests;
  final String? avatarUrl;

  User copyWith({
    String? name,
    String? budgetStyle,
    String? pace,
    List<String>? interests,
  }) => User(
    id: id,
    name: name ?? this.name,
    email: email,
    budgetStyle: budgetStyle ?? this.budgetStyle,
    pace: pace ?? this.pace,
    interests: interests ?? this.interests,
    avatarUrl: avatarUrl,
  );

  /// First letters of the first two words, or "?" for an empty name.
  String get initials {
    final words = name.trim().split(RegExp(r'\s+')).where((w) => w.isNotEmpty);
    if (words.isEmpty) return '?';
    return words.take(2).map((w) => w[0]).join().toUpperCase();
  }
}
