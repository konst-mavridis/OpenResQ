import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import 'package:uuid/uuid.dart';

class ApiService {
  final String baseUrl = "http://10.0.2.2:8000";

  Future<String> _getToken() async {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');

    final token = await user.getIdToken();
    if (token == null) throw Exception('Token is null');

    return token;
  }

  Future<Map<String, String>> _authHeaders() async {
    final token = await _getToken();
    return {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };
  }

  String _currentUid() {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('User not authenticated');
    return user.uid;
  }

  // ---------------------------------------------------------
  // REPORTS
  // ---------------------------------------------------------

  Future<List<dynamic>> getNearbyReports() async {
    final headers = await _authHeaders();
    final res = await http.get(Uri.parse('$baseUrl/reports/nearby'), headers: headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception(res.body);
  }

  Future<List<dynamic>> getAllReports() async {
    final headers = await _authHeaders();
    final res = await http.get(Uri.parse('$baseUrl/reports/all'), headers: headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception(res.body);
  }

  Future<List<dynamic>> getAssignedReports() async {
    final headers = await _authHeaders();
    final res = await http.get(Uri.parse('$baseUrl/reports/assigned'), headers: headers);
    if (res.statusCode == 200) return jsonDecode(res.body);
    throw Exception(res.body);
  }

  Future<Map<String, dynamic>> getReport(String id) async {
    final headers = await _authHeaders();
    final res = await http.get(Uri.parse('$baseUrl/reports/$id'), headers: headers);

    if (res.statusCode == 200) return jsonDecode(res.body);
    if (res.statusCode == 404) throw Exception("NOT_FOUND");

    throw Exception(res.body);
  }

  Future<Map<String, dynamic>> createReport(Map<String, dynamic> body) async {
    final headers = await _authHeaders();
    final res = await http.post(
      Uri.parse('$baseUrl/reports/'),
      headers: headers,
      body: jsonEncode(body),
    );

    if (res.statusCode >= 200 && res.statusCode < 300) {
      return jsonDecode(res.body);
    }

    throw Exception(res.body);
  }

  Future<void> responderUpdate(String id, Map<String, dynamic> patch) async {
    final headers = await _authHeaders();
    final res = await http.patch(
      Uri.parse('$baseUrl/reports/$id/respond'),
      headers: headers,
      body: jsonEncode(patch),
    );

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }
  }

  Future<void> deleteReport(
    String reportId, {
    required String reason,
    bool hard = false,
    bool confirm = false,
  }) async {
    final uri = Uri.parse(
      '$baseUrl/admin/report/$reportId'
      '?reason=${Uri.encodeComponent(reason)}'
      '&hard=$hard'
      '&confirm=$confirm',
    );

    final res = await http.delete(uri, headers: await _authHeaders());

    if (res.statusCode != 200) throw Exception(res.body);
  }

  Future<void> editOwnReport(String id, Map<String, dynamic> patch) async {
    final res = await http.patch(
      Uri.parse('$baseUrl/reports/$id/edit'),
      headers: await _authHeaders(),
      body: jsonEncode(patch),
    );

    if (res.statusCode != 200) throw Exception(res.body);
  }

  Future<void> deleteOwnReport(String id, String reason) async {
    final res = await http.delete(
      Uri.parse('$baseUrl/reports/$id/delete?reason=${Uri.encodeComponent(reason)}'),
      headers: await _authHeaders(),
    );

    if (res.statusCode != 200) throw Exception(res.body);
  }

  // ---------------------------------------------------------
  // CHAT
  // ---------------------------------------------------------

  Future<List<dynamic>> getChatMessages(String id) async {
    final res = await http.get(
      Uri.parse('$baseUrl/reports/$id/chat'),
      headers: await _authHeaders(),
    );

    if (res.statusCode != 200) throw Exception('Failed to load chat');

    return jsonDecode(res.body);
  }

  Future<void> sendChatMessage(String id, String text) async {
    final res = await http.post(
      Uri.parse('$baseUrl/reports/$id/chat'),
      headers: await _authHeaders(),
      body: jsonEncode({"text": text}),
    );

    if (res.statusCode != 200) throw Exception('Failed to send message');
  }

  Future<void> markChatSeen(String reportId) async {
    await http.post(
      Uri.parse("$baseUrl/reports/$reportId/chat/seen"),
      headers: await _authHeaders(),
    );
  }

  Future<void> sendPushToken(String token) async {
    await http.post(
      Uri.parse("$baseUrl/report/push-token"),
      headers: {"Content-Type": "application/json"},
      body: json.encode({"push_token": token}),
    );
  }

  // ---------------------------------------------------------
  // USER
  // ---------------------------------------------------------

  Future<Map<String, dynamic>> getMe() async {
    final headers = await _authHeaders();
    final res = await http.get(Uri.parse('$baseUrl/auth/me'), headers: headers);

    if (res.statusCode == 200) return jsonDecode(res.body);

    final user = FirebaseAuth.instance.currentUser;
    return {'uid': user?.uid, 'email': user?.email};
  }

  Future<void> setOnDuty(String uid) async {
    await http.post(
      Uri.parse('$baseUrl/responders/$uid/on_duty'),
      headers: await _authHeaders(),
    );
  }

  Future<void> setOffDuty(String uid) async {
    await http.post(
      Uri.parse('$baseUrl/responders/$uid/off_duty'),
      headers: await _authHeaders(),
    );
  }

  Future<void> updateMyArea({
    required double latitude,
    required double longitude,
    double radiusKm = 25,
  }) async {
    final headers = await _authHeaders();

    final res = await http.put(
      Uri.parse(
        '$baseUrl/user/me/area?latitude=$latitude&longitude=$longitude&radius_km=$radiusKm',
      ),
      headers: headers,
    );

    if (res.statusCode != 200) throw Exception(res.body);
  }

  Future<void> resolveReport(String reportId, String uid) async {
    final uri = Uri.parse(
      "$baseUrl/reports/$reportId/resolve?responder_uid=$uid",
    );
    final headers = await _authHeaders();
    final res = await http.post(uri, headers: headers);
    if (res.statusCode != 200) throw Exception(res.body);
  }


  Future<void> claimReport(String reportId) async {
    final headers = await _authHeaders();
    final res = await http.patch(
      Uri.parse('$baseUrl/reports/$reportId/claim'),
      headers: headers,
    );

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }
  }

  // ---------------------------------------------------------
  // AUTO-SUGGEST SYSTEM (NEW)
  // ---------------------------------------------------------

  Future<void> manualAssignReport(String reportId) async {
    final uid = _currentUid();
    final res = await http.post(
      Uri.parse('$baseUrl/reports/$reportId/assign?responder_uid=$uid'),
      headers: await _authHeaders(),
    );

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }
  }

  Future<Map<String, dynamic>?> suggestForResponder({
    required String responderUid,
    required double lat,
    required double lng,
  }) async {
    final headers = await _authHeaders();

    final uri = Uri.parse(
      '$baseUrl/reports/suggest_for_responder'
      '?responder_uid=$responderUid'
      '&lat=$lat'
      '&lng=$lng',
    );

    final res = await http.post(uri, headers: headers);

    if (res.statusCode != 200) {
      throw Exception(res.body);
    }

    final data = jsonDecode(res.body);

    // ΠΑΝΤΑ επιστρέφουμε ΟΛΟ το JSON
    // ακόμα κι αν suggested == null
    return Map<String, dynamic>.from(data);
  }

  Future<void> acceptSuggestedReport(String reportId) async {
    final uid = _currentUid();
    final res = await http.post(
      Uri.parse('$baseUrl/reports/$reportId/accept_suggest?responder_uid=$uid'),
      headers: await _authHeaders(),
    );

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }
  }

  Future<void> rejectSuggestedReport(String reportId) async {
    final uid = _currentUid();
    final res = await http.post(
      Uri.parse('$baseUrl/reports/$reportId/reject_suggest?responder_uid=$uid'),
      headers: await _authHeaders(),
    );

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }
  }

  // ---------------------------------------------------------
  // ADMIN
  // ---------------------------------------------------------

  Future<List<dynamic>> getLogs({int limit = 50}) async {
    final headers = await _authHeaders();
    final uri = Uri.parse('$baseUrl/admin/logs?limit=$limit');

    final res = await http.get(uri, headers: headers);

    if (res.statusCode == 200) return jsonDecode(res.body);

    throw Exception(res.body);
  }

  Future<List<Map<String, dynamic>>> fetchResponders() async {
    final res = await http.get(
      Uri.parse('$baseUrl/admin/responders/'),
      headers: await _authHeaders(),
    );

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }

    final body = jsonDecode(res.body);
    return List<Map<String, dynamic>>.from(body is List ? body : []);
  }

  Future<void> addResponder(Map<String, dynamic> data, String uid) async {
    final res = await http.post(
      Uri.parse('$baseUrl/admin/responders/$uid/add'),
      headers: await _authHeaders(),
      body: jsonEncode(data),
    );

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }
  }

  Future<void> removeResponder(String uid) async {
    final res = await http.post(
      Uri.parse('$baseUrl/admin/responders/$uid/remove'),
      headers: await _authHeaders(),
    );

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }
  }

  Future<Map<String, dynamic>> fetchAdminStats() async {
    final res = await http.get(
      Uri.parse('$baseUrl/admin/analytics/stats'),
      headers: await _authHeaders(),
    );

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }

    return jsonDecode(res.body);
  }

  Future<List<Map<String, dynamic>>> fetchHeatmapPoints(String hazard) async {
    final res = await http.get(
      Uri.parse('$baseUrl/admin/analytics/heatmap/$hazard'),
      headers: await _authHeaders(),
    );

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }

    final body = jsonDecode(res.body);
    return List<Map<String, dynamic>>.from(
      (body is Map ? body['points'] : null) ?? [],
    );
  }

  Future<List<dynamic>> getReportsForReview() async {
    final headers = await _authHeaders();

    final res = await http.get(
      Uri.parse('$baseUrl/adminr/reports/for-review'),
      headers: headers,
    );

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }

    return jsonDecode(res.body);
  }

  Future<void> decision(String reportId, String decision) async {
    final headers = await _authHeaders();

    final uri = Uri.parse(
      '$baseUrl/adminr/reports/$reportId/decision',
    ).replace(queryParameters: {"decision": decision});

    final res = await http.post(uri, headers: headers);

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }
  }

  Future<Map<String, dynamic>> vote(
    String reportId,
    int vote, {
    double? userLat,
    double? userLng,
  }) async {
    final headers = await _authHeaders();
    final uid = _currentUid();
    final deviceFp = const Uuid().v4();

    final uri = Uri.parse('$baseUrl/votes/$reportId').replace(
      queryParameters: {
        'voter_id': uid,
        'vote': vote.toString(),
        'device_fp': deviceFp,
        if (userLat != null) 'lat': userLat.toString(),
        if (userLng != null) 'lng': userLng.toString(),
      },
    );

    final res = await http.post(
      uri,
      headers: headers,
    );

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception(res.body);
    }

    return jsonDecode(res.body);
  }

  Future<void> unassignReport(String reportId) async {
      final uri = Uri.parse('$baseUrl/reports/$reportId/unassign');
      final headers = await _authHeaders();

      final res = await http.post(
        uri,
        headers: headers,
      );

      if (res.statusCode < 200 || res.statusCode >= 300) {
        throw Exception(res.body);
      }
  }
}