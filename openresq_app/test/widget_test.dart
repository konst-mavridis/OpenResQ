import 'package:flutter_test/flutter_test.dart';
import 'package:openresq_app/main.dart'; // προσαρμοσέ το αν χρειάζεται

void main() {
  testWidgets('App loads', (WidgetTester tester) async {
    await tester.pumpWidget(const OpenResQApp());
    await tester.pumpAndSettle();
    expect(find.text('OpenResQ Login'), findsOneWidget);
  });
}