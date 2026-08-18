import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile/main.dart';

void main() {
  testWidgets('Home screen shows title and connection button', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('AI Tourism Platform Mobile App'), findsWidgets);
    expect(find.text('Check Backend Connection'), findsOneWidget);
  });
}
