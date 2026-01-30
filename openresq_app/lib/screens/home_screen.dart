import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../models/report.dart';
import '../screens/report_detail.dart';
import '../widgets/marker_popup.dart';
import 'login_screen.dart';
import '../widgets/report_form.dart';
import 'logs_screen.dart';
import 'package:geolocator/geolocator.dart';
import 'dart:async';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../services/live_reports_service.dart';
import 'reviewReports.dart';
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;
  final ApiService api = ApiService();
  final AuthService auth = AuthService();
  List<Report> reports = [];
  List<Report> filteredReports = [];
  String role = 'citizen';
  String? severityFilter;
  bool _isSatellite = false;
  LatLng? _userLocation;
  double _accuracy = 0;
  StreamSubscription<Position>? _positionStream;
  bool _followUser = true; // για auto-follow
  Report? _selectedReport;
  final LiveReportsService live = LiveReportsService();
  StreamSubscription? _liveSub;
  final GlobalKey<RefreshIndicatorState> _refreshKey =
  GlobalKey<RefreshIndicatorState>();



  final MapController _mapController = MapController();
  @override
  void initState() {
    super.initState();
    _initApp();
    _liveSub = live.connect().listen(
      (event) {
        final id = event["id"];
        final type = event["type"];
        final data = event["data"];

        setState(() {
          if (type == "MODIFIED") {
            final index = reports.indexWhere((r) => r.id == id);
            if (index != -1) {
              reports[index] = reports[index].copyWithFromMap(data);
            }
          }

          if (type == "ADDED") {
            reports.add(Report.fromJson({"id": id, ...data}));
          }

          if (type == "REMOVED") {
            reports.removeWhere((r) => r.id == id);
          }

          if (type == "report_assigned") {
            final reportId= event["report_id"];
            final assignedTo = event["assigned_to"];

            final index = reports.indexWhere((r) => r.id == reportId);
            if (index != -1) {
              reports[index] = reports[index].copyWithAssigned(assignedTo);
            }

            if (assignedTo == auth.uid) {
              filteredReports = reports.where((r) => r.assignedTo == auth.uid).toList();
            }
          }

          _applyFilter();
        });

        _refreshKey.currentState?.show();

      },
      onError: (err) async {
        debugPrint("Live stream lost, fallback to polling");
        await loadReports(); // ⬅️ ΤΟ D ΕΙΝΑΙ ΕΔΩ
      },
    );


  }
  Future<void> _initApp() async {
    await _goToUserLocation();   // ⬅️ ΠΡΩΤΑ location
    _startLiveLocation();        // μετά live tracking
    await loadUserAndReports();  // ⬅️ ΤΕΛΕΥΤΑΙΟ backend
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
        fetched = await api.getNearbyReports();
      } else {
        fetched = await api.getNearbyReports();
      }
      setState(() {
        reports = fetched.map((e) => Report.fromJson(e as Map<String,dynamic>)).toList();
        _applyFilter();
      });
    } catch (e) {
      print("Error loading reports: $e");
    }
  }

  Stream<List<Report>> getReportsStream() {
    return FirebaseFirestore.instance
        .collection('reports')
        .snapshots()
        .map((snapshot) => snapshot.docs
            .map((doc) => Report.fromJson(doc.data()))
            .toList());
  }


  Future<void> _logout() async {
    await auth.logout();

    if (!mounted) return;

    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  void _applyFilter() {
    if (severityFilter == null || severityFilter == 'All') {
      filteredReports = reports;
    } else {
      filteredReports = reports.where((r) => r.severity.toLowerCase() == severityFilter!.toLowerCase()).toList();
    }
  }

  Future<void> _goToUserLocation() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }

    if (permission == LocationPermission.deniedForever) return;

    final position = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );

    final latLng = LatLng(position.latitude, position.longitude);

    setState(() {
      _userLocation = latLng;
    });

    _mapController.move(latLng, 14.5);
    await api.updateMyArea(
      latitude: position.latitude,
      longitude: position.longitude,
      radiusKm: 25,
    );

  }

  Future<void> _startLiveLocation() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }

    if (permission == LocationPermission.deniedForever) return;

    _positionStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.best,
        distanceFilter: 5, // 🔥 update κάθε 5 μέτρα
      ),
    ).listen((Position position) {
      final latLng = LatLng(position.latitude, position.longitude);

      setState(() {
        _userLocation = latLng;
        _accuracy = position.accuracy;
      });

      if (_followUser) {
        _mapController.move(latLng, _mapController.camera.zoom);
      }
    });
  }

  @override
  void dispose() {
    _positionStream?.cancel();
    _liveSub?.cancel();
    super.dispose();
  }




  Color _severityColor(String? severity) {
    switch (severity?.toLowerCase()) {
      case 'low':
        return Colors.green.shade600;
      case 'medium':
        return Colors.orange.shade600;
      case 'high':
        return Colors.red.shade700;
      case 'critical':
        return Colors.purple.shade700;
      default:
        return Colors.grey.shade600;
    }
  }

  Offset _getPopupPosition(Report report) {
    final projected = _mapController.camera.project(
      LatLng(report.latitude, report.longitude),
    );

    final origin = _mapController.camera.pixelOrigin;

    return Offset(
      projected.x - origin.x - 100, // κέντρο popup
      projected.y - origin.y - 120, // πάνω από marker
    );
  }


  List<Widget> get _pages => [
        _buildReportsPage(),
        const LogsPage(), // το page που φτιάξαμε
        const ReviewReportsPage(),
      ];

  void _onSelectPage(int index) {
    setState(() => _selectedIndex = index);
    Navigator.pop(context); // κλείνει το drawer
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
    appBar: AppBar(
      title: const Text('OpenResQ'),
      actions: [
        IconButton(
          icon: Icon(_isSatellite ? Icons.map : Icons.satellite),
          tooltip: _isSatellite ? 'Normal map' : 'Satellite map',
          onPressed: () {
            setState(() {
              _isSatellite = !_isSatellite;
            });
          },
        ),

        IconButton(
          icon: const Icon(Icons.logout),
          tooltip: 'Logout',
          onPressed: () async {
            final confirm = await showDialog<bool>(
              context: context,
              builder: (ctx) => AlertDialog(
                title: const Text('Logout'),
                content: const Text('Θέλεις σίγουρα να αποσυνδεθείς;'),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(ctx, false),
                    child: const Text('Ακύρωση'),
                  ),
                  ElevatedButton(
                    onPressed: () => Navigator.pop(ctx, true),
                    child: const Text('Logout'),
                  ),
                ],
              ),
            );

            if (confirm == true) {
              await _logout();
            }
          },
        ),
      ],
    ),
      drawer: Drawer(
        child: ListView(
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(color: Colors.blue),
              child: Text('Menu', style: TextStyle(color: Colors.white, fontSize: 24)),
            ),
            ListTile(
              leading: const Icon(Icons.report),
              title: const Text("Reports"),
              onTap: () => _onSelectPage(0),
            ),
            if (role == 'admin')
              ListTile(
                leading: const Icon(Icons.list_alt),
                title: const Text("Logs"),
                onTap: () => _onSelectPage(1),
              ),
            if (role == 'admin')
              ListTile(
                leading: const Icon(Icons.check_circle),
                title: const Text("Review Reports"),
                onTap: () => _onSelectPage(2),
              ),
          ],
        ),
      ),
      body: _pages[_selectedIndex],
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

  Widget _buildReportsPage() {
    return Column(
      children: [
        Chip(label: const Text('25km radius'), avatar: const Icon(Icons.my_location, size: 16)),
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: 
          DropdownButton<String>(
            value: severityFilter ?? 'All',
            items: const [
              DropdownMenuItem(value: 'All', child: Text('All severities')),
              DropdownMenuItem(value: 'low', child: Text('Low')),
              DropdownMenuItem(value: 'medium', child: Text('Medium')),
              DropdownMenuItem(value: 'high', child: Text('High')),
            ],
            onChanged: (value) {
              setState(() {
                severityFilter = value;
                _applyFilter();
              });
            },
          ),
        ),
        SizedBox(
          height: 300,
          child: Stack(
           children: [ 
            FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: filteredReports.isNotEmpty
                    ? LatLng(filteredReports.first.latitude, filteredReports.first.longitude)
                    : LatLng(37.9838, 23.7275),
                initialZoom: 12.0,
              ),
              children: [
                TileLayer(
                  urlTemplate: _isSatellite
                      ? "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token=pk.eyJ1Ijoia29ubWF2ciIsImEiOiJjbWpvOHQ5bjcwOHpwM2ZxeDZ4amtyaTI2In0.4ht_QxTceiooKIRsy6kzxA"
                      : "https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=pk.eyJ1Ijoia29ubWF2ciIsImEiOiJjbWpvOHQ5bjcwOHpwM2ZxeDZ4amtyaTI2In0.4ht_QxTceiooKIRsy6kzxA",
                  userAgentPackageName: 'com.openresq.app',
                ),

          
  
                MarkerLayer(
                  markers: [
                    ...filteredReports.map((r) => Marker(
                      point: LatLng(r.latitude, r.longitude),
                      width: 40,
                      height: 40,
                      child: GestureDetector(
                        onTap: () {
                          _mapController.move(
                            LatLng(r.latitude, r.longitude),
                            15,
                          );

                          setState(() {
                            _selectedReport = r;
                            _followUser = false;
                          });
                        },
                        child: Icon(
                          Icons.location_on,
                          color: _severityColor(r.severity),
                          size: 40,
                        ),
                      ),
                      ),
                    ),
                    if (_userLocation != null)
                      Marker(
                        point: _userLocation!,
                        width: 18,
                        height: 18,
                        child: Container(
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: Colors.blue,
                            border: Border.all(color: Colors.white, width: 3),
                          ),
                        ),
                      ),

                  ],
                ),
                CircleLayer(
                  circles: [
                    if (_userLocation != null)
                      CircleMarker(
                        point: _userLocation!,
                        radius: _accuracy, // σε meters
                        useRadiusInMeter: true,
                        color: Colors.blue.withOpacity(0.15),
                        borderStrokeWidth: 1,
                        borderColor: Colors.blue.withOpacity(0.4),
                      ),
                  ],
                ),
                if (_selectedReport != null) ...[
                  Builder(builder: (context){
                    final pos = _getPopupPosition(_selectedReport!);
                    return Positioned(
                      left: pos.dx,
                      top: pos.dy,
                      child: MarkerPopup(
                        report: _selectedReport!,
                        mapController: _mapController,
                        onClose: () {
                          setState(() => _selectedReport = null);
                        },
                        onDetails: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => ReportDetail(
                                reportId: _selectedReport!.id,
                                role: role,
                              ),
                            ),
                          );
                        },
                        role: role,
                      ),
                    );
                  })

              ],
           ],),

                  Positioned(
                    bottom: 16,
                    right: 16,
                    child: FloatingActionButton(
                      mini: true,
                      backgroundColor: Colors.white,
                      onPressed: () async {
                        _followUser = true;
                        await _goToUserLocation();
                      },
                      child: const Icon(
                        Icons.my_location,
                        color: Colors.blue,
                      ),
                    ),
                  ),

           ]
          )        
        ),
        Expanded(
          child: RefreshIndicator(
            key: _refreshKey,
            onRefresh: loadReports,
            child: ListView.builder(
              itemCount: filteredReports.length,
              itemBuilder: (context, i) {
                final r = filteredReports[i];
                return ListTile(
                  leading: Icon(Icons.circle, size: 12, color: _severityColor(r.severity)),
                  title: Text(r.title),
                  subtitle: Text('${r.eventType} • ${r.severity} • ${r.status}'),
                  onTap: () {
                    final latLng = LatLng(r.latitude, r.longitude);

                      _mapController.move(latLng, 15);

                    setState(() {
                      _selectedReport = r;
                        _followUser = false;
                      });
                    },
                );
              },
            ),
          ),
        ),
      ],
    );
  }

}
