import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../../services/api_service.dart';
import '../../services/live_responders_service.dart';
import 'admin_requests_screen.dart';
import 'logs_screen.dart';
import 'admin_service_priority.dart';
import 'admin_teams.dart';

class SuperAdminDashboardPage extends StatefulWidget {
  const SuperAdminDashboardPage({super.key});

  @override
  State<SuperAdminDashboardPage> createState() => _SuperAdminDashboardPageState();
}

class _SuperAdminDashboardPageState extends State<SuperAdminDashboardPage> {
  final api = ApiService();
  final liveResponders = LiveRespondersService();

  StreamSubscription? _responderStream;
  StreamSubscription<Position>? _adminLocationStream;
  StreamSubscription? _firestoreResponderStream;

  Map<String, dynamic> stats = {};
  List<Map<String, dynamic>> responders = [];
  List<Map<String, dynamic>> reports = [];
  List<Map<String, dynamic>> admins = [];
  List<Map<String, dynamic>> teams = [];

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
      admins = await fetchAdmins();
      teams = await fetchTeams();
      loading = false;
      setState(() {});
    } catch (e) {
      setState(() {
        error = e.toString();
        loading = false;
      });
    }
  }

  Future<List<Map<String, dynamic>>> fetchAdmins() async {
    final snapshot = await FirebaseFirestore.instance
        .collection("users")
        .where("role", isEqualTo: "admin")
        .get();
    return snapshot.docs.map((d) => d.data()..['uid'] = d.id).toList();
  }

  Future<List<Map<String, dynamic>>> fetchTeams() async {
    final snapshot = await FirebaseFirestore.instance.collection("teams").get();
    return snapshot.docs.map((d) => d.data()..['id'] = d.id).toList();
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
            data['uid'] = d.id;
            return data;
          }).toList();
          setState(() {});
        });
  }

  // -----------------------------
  // LIVE RESPONDERS (WEBSOCKET)
  // -----------------------------
  void _startResponderStream() {
    liveResponders.connect().then((stream) {
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
      color: color.withValues(alpha: 0.9),
      borderStrokeWidth: 2,
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
        accuracy: LocationAccuracy.high,
        distanceFilter: 10,
      ),
    ).listen((Position newPos) {
      setState(() => _adminLocation = LatLng(newPos.latitude, newPos.longitude));
    });
  }

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (error != null) {
      return Scaffold(
        appBar: AppBar(title: const Text("Super Admin Dashboard")),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text("Error: $error"),
              ElevatedButton(
                onPressed: loadAll,
                child: const Text("Retry"),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text("Super Admin Dashboard"),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: loadAll,
          ),
        ],
      ),
      drawer: _buildDrawer(),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Stats Overview
            _buildStatsGrid(),
            // Map View
            _buildMapView(),
            // Admins List
            _buildAdminsSection(),
            // Teams Overview
            _buildTeamsSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildDrawer() {
    return Drawer(
      child: ListView(
        children: [
          const DrawerHeader(
            child: Text("Super Admin Menu", style: TextStyle(fontSize: 24)),
          ),
          ListTile(
            title: const Text("Manage Responders"),
            onTap: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const AdminResponderRequestsScreen()),
            ),
          ),
          ListTile(
            title: const Text("View Logs"),
            onTap: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const LogsPage()),
            ),
          ),
          ListTile(
            title: const Text("Service Priority"),
            onTap: _handleServicePriority,
          ),
          ListTile(
            title: const Text("Manage Teams"),
            onTap: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const TeamsScreen()),
            ),
          ),
          ListTile(
            title: const Text("System Settings"),
            onTap: () {
              // TODO: Implement system settings
            },
          ),
          ListTile(
            title: const Text("Logout"),
            onTap: () async {
              await FirebaseAuth.instance.signOut();
              if (mounted) {
                Navigator.of(context).pushReplacementNamed('/');
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildStatsGrid() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: GridView.count(
        crossAxisCount: 2,
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        children: [
          _buildStatCard("Total Reports", stats["total_reports"]?.toString() ?? "0"),
          _buildStatCard("Active Responders", responders.where((r) => r["on_duty"] == true).length.toString()),
          _buildStatCard("Total Admins", admins.length.toString()),
          _buildStatCard("Total Teams", teams.length.toString()),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(value, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            Text(title, textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }

  Widget _buildMapView() {
    return SizedBox(
      height: 300,
      child: FlutterMap(
        mapController: _map,
        options: MapOptions(
          initialCenter: _adminLocation ?? const LatLng(37.7749, -122.4194),
          initialZoom: 10,
        ),
        children: [
          TileLayer(
            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            userAgentPackageName: 'com.example.app',
          ),
          CircleLayer(circles: responderCircles),
          if (_adminLocation != null)
            MarkerLayer(
              markers: [
                Marker(
                  width: 80.0,
                  height: 80.0,
                  point: _adminLocation!,
                  child: const Icon(Icons.location_on, color: Colors.red),
                ),
              ],
            ),
        ],
      ),
    );
  }

  Widget _buildAdminsSection() {
    return ExpansionTile(
      title: const Text("Admins Management"),
      children: [
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: admins.length,
          itemBuilder: (context, index) {
            final admin = admins[index];
            return ListTile(
              title: Text(admin["displayName"] ?? admin["email"]),
              subtitle: Text(admin["email"]),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(Icons.edit),
                    onPressed: () => _editAdmin(admin),
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete),
                    onPressed: () => _removeAdmin(admin["uid"]),
                  ),
                ],
              ),
            );
          },
        ),
        ListTile(
          title: const Text("Add New Admin"),
          leading: const Icon(Icons.add),
          onTap: _addAdmin,
        ),
      ],
    );
  }

  Widget _buildTeamsSection() {
    return ExpansionTile(
      title: const Text("Teams Overview"),
      children: [
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: teams.length,
          itemBuilder: (context, index) {
            final team = teams[index];
            return ListTile(
              title: Text(team["name"] ?? "Unnamed Team"),
              subtitle: Text("Members: ${team["member_count"] ?? 0}"),
              trailing: IconButton(
                icon: const Icon(Icons.info),
                onPressed: () => _viewTeamDetails(team),
              ),
            );
          },
        ),
      ],
    );
  }

  void _editAdmin(Map<String, dynamic> admin) {
    // TODO: Implement edit admin dialog
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Edit admin functionality coming soon")),
    );
  }

  void _removeAdmin(String uid) async {
    try {
      await FirebaseFirestore.instance.collection("users").doc(uid).update({"role": "citizen"});
      loadAll();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Admin removed successfully")),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error removing admin: $e")),
        );
      }
    }
  }

  void _addAdmin() {
    // TODO: Implement add admin dialog
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Add admin functionality coming soon")),
    );
  }

  void _handleServicePriority() async {
    if (_adminLocation == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Admin location not available")),
        );
      }
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
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("No teams found in your area")),
        );
      }
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

    if (selected != null && mounted) {
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
  }

  void _viewTeamDetails(Map<String, dynamic> team) {
    // TODO: Implement team details view
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Team details view coming soon")),
      );
    }
  }
}