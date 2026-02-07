import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import 'package:fl_chart/fl_chart.dart';

import '../../services/api_service.dart';
import '../../services/live_responders_service.dart';
import '../widgets/stat_card.dart';
import '../widgets/responder_tile.dart';

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

  Map<String, dynamic> stats = {};
  List<Map<String, dynamic>> responders = [];
  List<Map<String, dynamic>> reports = [];

  LatLng? _adminLocation;

  bool loading = true;
  String? error;

  final MapController _map = MapController();

  // Live responder circles
  final List<CircleMarker> responderCircles = [];

  @override
  void initState() {
    super.initState();
    loadAll();
    _startAdminLocation();
    _startResponderStream();
  }

  @override
  void dispose() {
    _responderStream?.cancel();
    _adminLocationStream?.cancel();
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
      responders = List<Map<String, dynamic>>.from(await api.fetchResponders());
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
  // LIVE RESPONDERS
  // -----------------------------
  void _startResponderStream() {
    _responderStream = liveResponders.connect().listen((event) {
      final type = event["type"];
      final data = event["data"];

      if (type == "responder_status" ||
          type == "responder_moved" ||
          type == "responder_added") {
        _updateResponderCircle(data);
      }

      if (type == "responder_removed") {
        responderCircles.removeWhere(
            (c) => c.key == ValueKey(event["uid"]));
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

      // Auto-center
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
        const Text("Reports Severity Breakdown",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
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
  // HEATMAP (SEPARATE)
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
        const Text("Reports per Hour (Heatmap Style)",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
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
          IconButton(icon: const Icon(Icons.refresh), onPressed: loadAll),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (error != null)
              Text(error!, style: const TextStyle(color: Colors.red)),

            const SizedBox(height: 12),

            // -----------------------------
            // MAP
            // -----------------------------
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

                  // Responders
                  CircleLayer(circles: responderCircles),

                  // Admin
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

            // -----------------------------
            // CHARTS
            // -----------------------------
            _buildCharts(),
            const SizedBox(height: 20),
            _buildHeatmap(),

            const SizedBox(height: 20),

            // -----------------------------
            // RESPONDERS LIST
            // -----------------------------
            const Text("Responders",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),

            ...responders.map(
              (r) => ResponderTile(
                responder: r,
                onRemove: () async {
                  await api.removeResponder(r['uid']);
                  loadAll();
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
