// Basic Flutter widget test for SatyVaani app

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:satyavani_app/main.dart';

void main() {
  testWidgets('SatyVaani app smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const SatyVaaniApp());

    // Verify the app loads (login screen should appear)
    expect(find.text('SatyVaani'), findsOneWidget);
  });
}
