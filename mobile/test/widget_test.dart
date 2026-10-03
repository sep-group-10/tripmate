import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app.dart';

/// The async route redirect and the mock delays run on timers, so let fake
/// time pass before settling frames.
Future<void> _settle(WidgetTester tester) async {
  await tester.pump(const Duration(seconds: 1));
  await tester.pumpAndSettle();
}

/// A tall phone-width surface, so lazily built list content is on screen.
void _tallPhone(WidgetTester tester) {
  tester.view
    ..physicalSize = const Size(400, 6000)
    ..devicePixelRatio = 1;
  addTearDown(tester.view.reset);
}

Future<void> _logIn(WidgetTester tester) async {
  _tallPhone(tester);
  await tester.pumpWidget(const TripMateApp(useWebFonts: false));
  await _settle(tester);
  expect(find.text('Welcome back'), findsOneWidget);

  await tester.enterText(find.byType(TextField).first, 'nimali@example.com');
  await tester.enterText(find.byType(TextField).last, 'password123');
  await tester.tap(find.text('Log in'));
  await _settle(tester);
}

void main() {
  testWidgets('signed-out users land on the login page', (tester) async {
    await tester.pumpWidget(const TripMateApp(useWebFonts: false));
    await _settle(tester);
    expect(find.text('Welcome back'), findsOneWidget);
    expect(find.text('Log in'), findsOneWidget);
  });

  testWidgets('log in shows the three web sections and My trips groups', (
    tester,
  ) async {
    await _logIn(tester);

    for (final label in ['Chat', 'My trips', 'Profile']) {
      expect(find.text(label), findsWidgets);
    }
    expect(find.text('Explore'), findsNothing);
    expect(find.text('TRIP PLANNER'), findsOneWidget);

    await tester.tap(find.text('My trips').last);
    await _settle(tester);
    expect(find.text('Saved trips'), findsOneWidget);
    expect(find.text('Generated itineraries'), findsOneWidget);
    expect(find.text('UPCOMING'), findsNothing);
    expect(find.text('COMPLETED'), findsNothing);
  });

  testWidgets('chat plans a trip and enables Save trip', (tester) async {
    await _logIn(tester);
    await tester.enterText(find.byType(TextField).last, 'plan a trip');
    await tester.pump(); // the send button enables on rebuild
    await tester.tap(find.byIcon(Icons.send_rounded));
    await tester.pumpAndSettle(const Duration(seconds: 2));
    expect(find.textContaining('Your trip plan is ready.'), findsOneWidget);

    await tester.tap(find.text('Save trip'));
    await tester.pumpAndSettle();
    expect(find.text('Saved'), findsOneWidget);
  });
}
