import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import 'local_queue.dart'; // we'll implement sqflite queue

class ApiService {
  final String baseUrl = "http://10.0.2.2:8000";
  final LocalQueue _queue = LocalQueue();

  Future<String> _getToken() async {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception("Not logged in");
    final token = await user.getIdToken();
    if (token == null) throw Exception("Failed to get id token");
    return token;
  }

  Map<String,String> _authHeaders(String token) => {
    "Content-Type": "application/json",
    "Authorization": "Bearer $token",
  };

  Future<Map<String,dynamic>> createReport(Map<String,dynamic> body) async {
    final token = await _getToken();
    try {
      final resp = await http.post(Uri.parse("$baseUrl/reports/"),
        headers: _authHeaders(token),
        body: jsonEncode(body),
      ).timeout(const Duration(seconds: 8));
      if (resp.statusCode >=200 && resp.statusCode<300) return jsonDecode(resp.body);
      throw Exception(resp.body);
    } catch (e) {
      // enqueue for later if offline or error
      await _queue.enqueue({"path": "/reports/", "method":"POST", "body": body});
      rethrow; // optionally rethrow so UI knows it failed now
    }
  }

  Future<List<dynamic>> getNearbyReports() async {
    final token = await _getToken();
    final resp = await http.get(Uri.parse("$baseUrl/reports/nearby"),
      headers: _authHeaders(token),
    );
    if (resp.statusCode==200) return jsonDecode(resp.body) as List<dynamic>;
    throw Exception(resp.body);
  }

  Future<List<dynamic>> getAssignedReports() async {
    final token = await _getToken();
    final resp = await http.get(Uri.parse("$baseUrl/reports/assigned"),
      headers: _authHeaders(token),
    );
    if (resp.statusCode==200) return jsonDecode(resp.body) as List<dynamic>;
    throw Exception(resp.body);
  }

  Future<Map<String,dynamic>> getReport(String id) async {
    final token = await _getToken();
    final resp = await http.get(Uri.parse("$baseUrl/reports/$id"),
      headers: _authHeaders(token),
    );
    if (resp.statusCode==200) return jsonDecode(resp.body);
    throw Exception(resp.body);
  }

  Future<void> responderUpdate(String id, Map<String,dynamic> patch) async {
    final token = await _getToken();
    final resp = await http.patch(Uri.parse("$baseUrl/reports/$id/respond"),
      headers: _authHeaders(token),
      body: jsonEncode(patch),
    );
    if (resp.statusCode<200||resp.statusCode>=300) throw Exception(resp.body);
  }

  Future<void> deleteReport(String id) async => adminDelete(id);

  Future<void> adminDelete(String id) async {
    final token = await _getToken();
    final resp = await http.delete(Uri.parse("$baseUrl/admin/report/$id"),
      headers: _authHeaders(token),
    );
    if (resp.statusCode<200||resp.statusCode>=300) throw Exception(resp.body);
  }

  Future<Map<String,dynamic>> getMe() async {
    final token = await _getToken();
    final resp = await http.get(Uri.parse("$baseUrl/me"), headers: _authHeaders(token));
    if (resp.statusCode == 200) return jsonDecode(resp.body);
    // fallback: return basic firebase user info
    final user = FirebaseAuth.instance.currentUser;
    if (user != null) return {"uid": user.uid, "email": user.email};
    throw Exception(resp.body);
  }

  // process queued requests (call when connectivity returns or app starts)
  Future<void> processQueue() async {
    final items = await _queue.getAll();
    for (final item in items) {
      try {
        final token = await _getToken();
        final path = item['path'] as String;
        final method = item['method'] as String;
        final body = item['body'] as Map<String,dynamic>?;
        http.Response resp;
        if (method == "POST") {
          resp = await http.post(Uri.parse(baseUrl + path), headers: _authHeaders(token), body: jsonEncode(body ?? {}));
        } else {
          // add other methods as needed
          continue;
        }
        if (resp.statusCode >=200 && resp.statusCode < 300) {
          await _queue.remove(item['id'] as int);
        }
      } catch (_) {
        // stop processing if still offline / token fail
      }
    }
  }
}
