import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';

class LiveReportsService {
  final String baseUrl = "https://openresq.onrender.com";

  Stream<Map<String, dynamic>> connect() async* {
    final user = FirebaseAuth.instance.currentUser;
    final token = await user!.getIdToken();

    final request = http.Request(
      "GET",
      Uri.parse("$baseUrl/reports/nearby/live"),
    );

    request.headers["Authorization"] = "Bearer $token";

    final response = await request.send();

    await for (var line in response.stream
        .transform(utf8.decoder)
        .transform(const LineSplitter())) {
      if (line.startsWith("data: ")) {
        yield jsonDecode(line.substring(6));
      }
    }
  }
}
