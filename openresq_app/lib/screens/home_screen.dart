import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../models/report.dart';
import 'report_detail.dart';
import 'login_screen.dart';
import '../widgets/report_form.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService api = ApiService();
  final AuthService auth = AuthService();
  List<Report> reports = [];
  String role = "citizen";
  final MapController _mapController = MapController();

  @override
  void initState() {
    super.initState();
    loadUserAndReports();
  }

  Future<void> loadUserAndReports() async {
    // get role from backend
    try {
      final me = await api.getMe();
      role = me['role'] ?? 'citizen';
    } catch (_) {}
    await loadReports();
  }

  Future<void> loadReports() async {
    try {
      List<dynamic> fetched;
      if (role == 'responder') {
        fetched = await api.getAssignedReports();
      } else {
        fetched = await api.getNearbyReports();
      }
      setState(() {
        reports = fetched.map((e) => Report.fromJson(e as Map<String,dynamic>)).toList();
      });
    } catch (e) {
      print("Error loading reports: $e");
    }
  }

  Color _severityColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'high': return Colors.red;
      case 'medium': return Colors.orange;
      default: return Colors.green;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('OpenResQ'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () async {
              await auth.logout();
              if (context.mounted) {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (context) => const LoginScreen()),
                  (route) => false,
                );
              }
            },
          ),
        ],
      ),
      body:
        Column(
        children: [
          SizedBox(
            height: 300,
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: reports.isNotEmpty ? LatLng(reports.first.latitude, reports.first.longitude) : LatLng(37.9838,23.7275),
                initialZoom: 12.0,
              ),
              children: [
                TileLayer(urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', subdomains: ['a','b','c']),
                MarkerLayer(markers: reports.map((r) {
            return Marker(
                    point: LatLng(r.latitude, r.longitude),
                    width: 50, height: 50,
                    child: GestureDetector(
                      onTap: () {
                        Navigator.push(context, MaterialPageRoute(builder: (_) => ReportDetail(reportId: r.id, role: role))).then((_) => loadReports());
                      },
                      child: Icon(Icons.location_on, color: _severityColor(r.severity), size: 36),
                    ),
                  );
                }).toList())
              ],
            ),
          ),
          Expanded(
            child: RefreshIndicator(
              onRefresh: loadReports,
              child: ListView.builder(
                itemCount: reports.length,
                itemBuilder: (context, i) {
                  final r = reports[i];
                  return ListTile(
                    title: Text(r.title),
                    subtitle: Text('${r.eventType} • ${r.severity} • ${r.status}'),
                    onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ReportDetail(reportId: r.id, role: role))).then((_)=>loadReports()),
                  );
                },
              ),
            ),
          )
        ],
      ),
      floatingActionButton: role == 'citizen' ? FloatingActionButton(
        onPressed: () async {
          final result = await showModalBottomSheet<bool>(
            context: context,
            isScrollControlled: true,
            builder: (ctx) => const ReportForm(),
          );
          if (result == true) {
            await loadReports();
          }
        },
        child: const Icon(Icons.add),
      ) : null,
    );
  }
}
