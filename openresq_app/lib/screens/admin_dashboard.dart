import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:openresq_app/screens/admin_teams.dart';
import '../../services/api_service.dart';
import '../../services/live_responders_service.dart';
import '../widgets/responder_tile.dart';
import '../widgets/add_responder_dial.dart';
import '../screens/admin_requests_screen.dart';
import '../screens/logs_screen.dart';
import '../screens/admin_service_priority.dart';
class AdminDashboardPage extends StatefulWidget {
  const AdminDashboardPage({super.key});

  @override
  State<AdminDashboardPage> createState() => _AdminDashboardPageState();
}

class _AdminDashboardPageState extends State<AdminDashboardPage> {
  final api = ApiService();
  final liveResponders = LiveRespondersService();

  StreamSubscription? _responderStream;
  StreamSubscription<Position>? _adminLocationStream;
  StreamSubscription? _firestoreResponderStream;

  Map<String, dynamic> stats = {};
  List<Map<String, dynamic>> responders = [];
  List<Map<String, dynamic>> reports = [];

  LatLng? _adminLocation;

  bool loading = true;
  String? error;

  final MapController _map = MapController();

  final List<CircleMarker> responderCircles = [];

  @override
  void initState() {
    super.initState();
    loadAll();
    _startAdminLocation();
    _startResponderStream();
    _startFirestoreResponderListener();
  }

  @override
  void dispose() {
    _responderStream?.cancel();
    _adminLocationStream?.cancel();
    _firestoreResponderStream?.cancel();
    super.dispose();
  }

  // -----------------------------
  // LOAD DATA
  // -----------------------------
  Future<void> loadAll() async {
    setState(() {
      loading = true;
      error = null;
    });

    try {
      stats = await api.fetchAdminStats();
      reports = List<Map<String, dynamic>>.from(await api.getNearbyReports());

      loading = false;
      setState(() {});
    } catch (e) {
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  // -----------------------------
  // REAL-TIME RESPONDERS FROM FIRESTORE
  // -----------------------------
  void _startFirestoreResponderListener() {
    _firestoreResponderStream = FirebaseFirestore.instance
        .collection("users")
        .where("role", isEqualTo: "responder")
        .snapshots()
        .listen((snapshot) {
            responders = snapshot.docs.map((d) {
              final data = d.data();
              data['uid'] = d.id; // 🔥 Βάζουμε το UID σωστά
              return data;
            }).toList();
      setState(() {});
    });
  }

  // -----------------------------
  // LIVE RESPONDERS (WEBSOCKET)
  // -----------------------------
  void _startResponderStream() async {
    final stream = await liveResponders.connect();
    _responderStream = stream.listen((event) {
      final type = event["type"];
      final data = event["data"];

      if (type == "responder_status" ||
          type == "responder_moved" ||
          type == "responder_added") {
        _updateResponderCircle(data);
      }

      if (type == "responder_removed") {
        responderCircles.removeWhere(
          (c) => c.key == ValueKey(event["uid"]),
        );
      }

      setState(() {});
    });
  }

  void _updateResponderCircle(Map<String, dynamic> r) {
    final lat = r["area"]?["latitude"];
    final lng = r["area"]?["longitude"];
    final onDuty = r["on_duty"] == true;

    if (!onDuty) {
      responderCircles.removeWhere((c) => c.key == ValueKey(r["uid"]));
      return;
    }

    if (lat == null || lng == null) return;

    final hasActive = r["active_report_id"] != null;

    final color = hasActive ? Colors.green : Colors.blue;

    final circle = CircleMarker(
      key: ValueKey(r["uid"]),
      point: LatLng(lat.toDouble(), lng.toDouble()),
      radius: 8,
      color: color.withOpacity(0.9),
      borderStrokeWidth: 2,
      borderColor: Colors.white,
    );

    responderCircles.removeWhere((c) => c.key == ValueKey(r["uid"]));
    responderCircles.add(circle);
  }

  // -----------------------------
  // ADMIN LOCATION
  // -----------------------------
  void _startAdminLocation() {
    _adminLocationStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.best,
        distanceFilter: 5,
      ),
    ).listen((pos) {
      final newPos = LatLng(pos.latitude, pos.longitude);

      setState(() => _adminLocation = newPos);

      _map.move(newPos, 14);

      api.updateMyArea(
        latitude: pos.latitude,
        longitude: pos.longitude,
        radiusKm: 20,
      );
    });
  }

  // -----------------------------
  // CHARTS
  // -----------------------------
  Widget _buildCharts() {
    final severityCounts = {
      "low": 0,
      "medium": 0,
      "high": 0,
    };

    for (var r in reports) {
      final sev = r["severity"]?.toString().toLowerCase() ?? "low";
      if (severityCounts.containsKey(sev)) {
        severityCounts[sev] = severityCounts[sev]! + 1;
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "Reports Severity Breakdown",
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        SizedBox(
          height: 200,
          child: PieChart(
            PieChartData(
              sections: [
                PieChartSectionData(
                  value: severityCounts["low"]!.toDouble(),
                  color: Colors.green,
                  title: "Low",
                ),
                PieChartSectionData(
                  value: severityCounts["medium"]!.toDouble(),
                  color: Colors.orange,
                  title: "Medium",
                ),
                PieChartSectionData(
                  value: severityCounts["high"]!.toDouble(),
                  color: Colors.red,
                  title: "High",
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // -----------------------------
  // HEATMAP
  // -----------------------------
  Widget _buildHeatmap() {
    final List<FlSpot> spots = [];

    for (var r in reports) {
      final created = r["created_at"];
      if (created != null) {
        final hour = DateTime.parse(created).hour.toDouble();
        spots.add(FlSpot(hour, 1));
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "Reports per Hour (Heatmap Style)",
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        SizedBox(
          height: 200,
          child: LineChart(
            LineChartData(
              lineBarsData: [
                LineChartBarData(
                  spots: spots,
                  isCurved: true,
                  color: Colors.red,
                  barWidth: 3,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // -----------------------------
  // BUILD UI
  // -----------------------------
  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text("Admin Dashboard"),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: loadAll,
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await FirebaseAuth.instance.signOut();
              if (!mounted) return;
              Navigator.pushNamedAndRemoveUntil(
                context,
                '/',
                (route) => false,
              );
            },
          ),
        ],
      ),

      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(color: Colors.redAccent),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    "Admin Menu",
                    style: TextStyle(color: Colors.white, fontSize: 22),
                  ),
                  SizedBox(height: 8),
                  Text(
                    "Manage system settings",
                    style: TextStyle(color: Colors.white70),
                  ),
                ],
              ),
            ),

            ListTile(
              leading: const Icon(Icons.verified_user),
              title: const Text("Approve Responders"),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const AdminResponderRequestsScreen(),
                  ),
                );
              },
            ),

            ListTile(
              leading: const Icon(Icons.groups),
              title: const Text("Manage Teams"),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const TeamsScreen(),
                  ),
                );
              },
            ),

            ListTile(
              leading: const Icon(Icons.list_alt),
              title: const Text("System Logs"),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const LogsPage(),
                  ),
                );
              },
            ),

            ListTile(
              leading: const Icon(Icons.tune),
              title: const Text("Teams Priorities"),
              onTap: () async {
                Navigator.pop(context);

                if (_adminLocation == null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text("Admin location not available")),
                  );
                  return;
                }

                // Load teams from Firestore
                final snap = await FirebaseFirestore.instance
                    .collection("teams")
                    .get();

                final distance = Distance();
                final List<Map<String, dynamic>> teams = [];

                for (var doc in snap.docs) {
                  final data = doc.data();
                  final lat = data["area"]?["latitude"];
                  final lng = data["area"]?["longitude"];

                  if (lat != null && lng != null) {
                    final dist = distance(
                      _adminLocation!,
                      LatLng(lat.toDouble(), lng.toDouble()),
                    );

                    if (dist <= 25000) { // 25 km radius
                      teams.add({
                        "id": doc.id,
                        "name": data["name"] ?? "Unnamed Team",
                        "distance": dist,
                      });
                    }
                  }
                }

                if (teams.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text("No teams found in your area")),
                  );
                  return;
                }

                // Sort by distance
                teams.sort((a, b) => a["distance"].compareTo(b["distance"]));

                // Show dialog
                final selected = await showDialog<Map<String, dynamic>>(
                  context: context,
                  builder: (_) => SimpleDialog(
                    title: const Text("Select Team"),
                    children: teams.map((t) {
                      return SimpleDialogOption(
                        onPressed: () => Navigator.pop(context, t),
                        child: Text("${t["name"]} (${(t["distance"] / 1000).toStringAsFixed(1)} km)"),
                      );
                    }).toList(),
                  ),
                );

                if (selected != null && context.mounted) {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => AdminServicePriorityScreen(
                        serviceId: selected["id"],
                        serviceName: selected["name"],
                      ),
                    ),
                  );
                }
              },
            ),
           const Divider(),

            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text("Logout"),
              onTap: () async {
                await FirebaseAuth.instance.signOut();
                if (!context.mounted) return;
                Navigator.pushNamedAndRemoveUntil(
                  context,
                  '/',
                  (route) => false,
                );
              },
            ),
          ],
        ),
      ),

      body: SingleChildScrollView(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (error != null)
              Text(
                error!,
                style: const TextStyle(color: Colors.red),
              ),

            const SizedBox(height: 12),

            SizedBox(
              height: 300,
              child: FlutterMap(
                mapController: _map,
                options: MapOptions(
                  initialCenter: _adminLocation ?? LatLng(37.9838, 23.7275),
                  initialZoom: 12,
                ),
                children: [
                  TileLayer(
                    urlTemplate:
                        "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    userAgentPackageName: "openresq.admin",
                  ),

                  CircleLayer(circles: responderCircles),

                  if (_adminLocation != null)
                    CircleLayer(
                      circles: [
                        CircleMarker(
                          point: _adminLocation!,
                          radius: 10,
                          color: Colors.red.withOpacity(0.9),
                          borderStrokeWidth: 2,
                          borderColor: Colors.white,
                        ),
                      ],
                    ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            _buildCharts(),
            const SizedBox(height: 20),
            _buildHeatmap(),

            const SizedBox(height: 20),

            const Text(
              "Responders",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),

            ...responders.map(
              (r) => ResponderTile(
                responder: r,
                onRemove: () async {
                  final uid = r['uid'] as String;

                  // backend cleanup (αν το χρειάζεσαι)
                  await api.removeResponder(uid);

                  // Firestore: ο χρήστης παύει να είναι responder
                  await FirebaseFirestore.instance
                      .collection("users")
                      .doc(uid)
                      .update({"role": "citizen"});
                  // Το Firestore stream θα τον αφαιρέσει αυτόματα από τη λίστα
                },
              ),
            ),

            const SizedBox(height: 20),

            Center(
              child: ElevatedButton.icon(
                icon: const Icon(Icons.person_add),
                label: const Text("Add Responder"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 14,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (_) =>
                        AddResponderDialog(adminLocation: _adminLocation),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
