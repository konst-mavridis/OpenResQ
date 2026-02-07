import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/report.dart';
import '../screens/navigations_screen.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class ResponderHomePage extends StatefulWidget {
  const ResponderHomePage({super.key});

  @override
  State<ResponderHomePage> createState() => _ResponderHomePageState();
}

class _ResponderHomePageState extends State<ResponderHomePage> {
  final api = ApiService();
  final auth = AuthService();

  bool onDuty = false;

  LatLng? _userLocation;
  StreamSubscription<Position>? _posStream;

  List<Report> allReportsInArea = [];
  final MapController _map = MapController();
  Timer? _refreshTimer;

  String? activeReportId; // <-- NEW

  @override
  void initState() {
    super.initState();
    _init();

    _refreshTimer = Timer.periodic(const Duration(seconds: 10), (_) async {
      if (onDuty) {
        await _loadReportsInArea();
        await _checkAutoSuggest();
      }
    });
  }

  Future<void> _init() async {
    final prefs = await SharedPreferences.getInstance();
    onDuty = prefs.getBool("onDuty") ?? false;
    activeReportId = prefs.getString("activeReportId"); // <-- NEW
    final assigned = await api.getAssignedReports();
    if (assigned.isNotEmpty) {
      activeReportId = assigned.first["id"];
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString("activeReportId", activeReportId!);
    } else {
      activeReportId = null;
    }


    await _goToLocation();
    _startLiveLocation();
    await _loadReportsInArea();
    await _checkAutoSuggest();

    if (mounted) setState(() {});
  }

  Future<void> _goToLocation() async {
    final pos = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );

    final latLng = LatLng(pos.latitude, pos.longitude);
    setState(() => _userLocation = latLng);

    _map.move(latLng, 14);

    if (onDuty) {
      await api.updateMyArea(
        latitude: pos.latitude,
        longitude: pos.longitude,
        radiusKm: 20,
      );
    }
  }

  void _startLiveLocation() {
    _posStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.best,
        distanceFilter: 5,
      ),
    ).listen((pos) async {
      final latLng = LatLng(pos.latitude, pos.longitude);
      setState(() => _userLocation = latLng);

      if (onDuty) {
        await api.updateMyArea(
          latitude: pos.latitude,
          longitude: pos.longitude,
          radiusKm: 20,
        );
      }
    });
  }

  Future<void> _loadReportsInArea() async {
    if (!onDuty || _userLocation == null) {
      setState(() => allReportsInArea.clear());
      return;
    }

    final fetched = await api.getNearbyReports();
    setState(() {
      allReportsInArea = fetched.map((e) => Report.fromJson(e)).toList();
    });
  }

  Future<void> _checkAutoSuggest() async {
    if (!onDuty || _userLocation == null) return;

    final response = await api.suggestForResponder(
      responderUid: auth.uid!,
      lat: _userLocation!.latitude,
      lng: _userLocation!.longitude,
    );

    if (response == null || response["suggested"] == null) return;

    final reportJson = response["suggested"];
    final report = Report.fromJson(reportJson);

    // ΠΡΕΠΕΙ να ελέγξουμε το on_hold_for ΜΕΣΑ στο suggested
    if (reportJson["on_hold_for"] != auth.uid) return;

    if (!mounted) return;

    showDialog(
      context: context,
      builder: (_) {
        return AlertDialog(
          title: const Text("Νέο προτεινόμενο περιστατικό"),
          content: Text(
            "Severity: ${report.severity}\n"
            "Τίτλος: ${report.title}\n\n"
            "Θέλεις να το αναλάβεις;",
          ),
          actions: [
            TextButton(
              onPressed: () async {
                try {
                  await api.rejectSuggestedReport(report.id);
                } catch (e) {
                  print("REJECT ERROR: $e");
                }
                if (!mounted) return;
                Navigator.of(context).pop();
              },
              child: const Text("Όχι"),
            ),
            ElevatedButton(
              onPressed: () async {
                try {
                  await api.acceptSuggestedReport(report.id);
                } catch (e) {
                  print("ACCEPT ERROR: $e");
                }

                final prefs = await SharedPreferences.getInstance();
                await prefs.setString("activeReportId", report.id);
                activeReportId = report.id;

                if (!mounted) return;
                Navigator.of(context).pop();
                await _loadReportsInArea();
              },
              child: const Text("Ναι"),
            ),
          ],
        );
      },
    );
  }

  @override
  void dispose() {
    _posStream?.cancel();
    _refreshTimer?.cancel();
    super.dispose();
  }

  void _focusOnReport(Report r) {
    final point = LatLng(r.latitude, r.longitude);
    _map.move(point, 16);
    _openReportSheet(r);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Responder Dashboard"),
      ),
      body: Column(
        children: [
          if (activeReportId != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              color: Colors.green.shade600,
              child: Text(
                "Assigned report: $activeReportId",
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          if (activeReportId == null && onDuty)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              color: Colors.amber.shade600,
              child: const Text(
                "No active report assigned",
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              )
            ),
          _buildDutySwitch(),
          // _buildDebugButtons(), 
          _buildMap(),
          _buildReportsList(),
        ],
      ),
    );
  }

  Widget _buildDutySwitch() {
    return SwitchListTile(
      title: const Text("On Duty"),
      value: onDuty,
      onChanged: (value) async {
        setState(() => onDuty = value);

        final prefs = await SharedPreferences.getInstance();
        await prefs.setBool("onDuty", value);

        if (value) {
          await api.setOnDuty(auth.uid!);
          await _goToLocation();
          await _loadReportsInArea();
          await _checkAutoSuggest();
        } else {
          await api.setOffDuty(auth.uid!);
          activeReportId = null;
          await prefs.remove("activeReportId");
          setState(() => allReportsInArea.clear());
        }
      },
    );
  }

  Widget _buildMap() {
    return SizedBox(
      height: 300,
      child: FlutterMap(
        mapController: _map,
        options: MapOptions(
          initialCenter: _userLocation ?? LatLng(37.9838, 23.7275),
          initialZoom: 12,
        ),
        children: [
          TileLayer(
            urlTemplate: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            userAgentPackageName: "openresq.app",
          ),
          MarkerLayer(
            markers: [
              ...allReportsInArea.map(
                (r) => Marker(
                  point: LatLng(r.latitude, r.longitude),
                  width: 40,
                  height: 40,
                  child: GestureDetector(
                    onTap: () => _focusOnReport(r),
                    child: Icon(
                      Icons.warning,
                      color: r.id == activeReportId
                          ? Colors.green
                          : Colors.amber,
                      size: 40,
                    ),
                  ),
                ),
              ),
              if (_userLocation != null)
                Marker(
                  point: _userLocation!,
                  width: 20,
                  height: 20,
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
        ],
      ),
    );
  }

  void _openReportSheet(Report r) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (_) {
        final distText = _userLocation == null
            ? "--"
            : (Geolocator.distanceBetween(
                        _userLocation!.latitude,
                        _userLocation!.longitude,
                        r.latitude,
                        r.longitude) /
                    1000)
                .toStringAsFixed(2);

        final isMine = r.id == activeReportId;
        final isUnassigned = r.id != activeReportId;

        return Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                r.title,
                style:
                    const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              Text("Severity: ${r.severity}"),
              Text("Distance: $distText km"),
              Text("Status: ${r.status}"),
              const SizedBox(height: 16),
              Row(
                children: [
                  ElevatedButton.icon(
                    onPressed: _userLocation != null
                        ? () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => NavigationScreen(report: r),
                              ),
                            );
                          }
                        : null,
                    icon: const Icon(Icons.navigation),
                    label: const Text("Navigate"),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    onPressed: onDuty && isMine
                        ? () async {
                            await api.resolveReport(r.id, auth.uid!);

                            final prefs = await SharedPreferences.getInstance();
                            await prefs.remove("activeReportId");
                            activeReportId = null;

                            if (!mounted) return;
                            Navigator.pop(context);
                            await _loadReportsInArea();
                          }
                        : null,
                    icon: const Icon(Icons.check),
                    label: const Text("Resolve"),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    onPressed: onDuty && isUnassigned
                        ? () async {
                            await api.manualAssignReport(r.id);

                            final prefs = await SharedPreferences.getInstance();
                            await prefs.setString("activeReportId", r.id);
                            activeReportId = r.id;

                            if (!mounted) return;
                            Navigator.pop(context);
                            await _loadReportsInArea();
                          }
                        : null,
                    icon: const Icon(Icons.assignment),
                    label: const Text("Assign"),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildReportsList() {
    return Expanded(
      child: ListView.builder(
        itemCount: allReportsInArea.length,
        itemBuilder: (_, i) {
          final r = allReportsInArea[i];
          final isMine = r.id == activeReportId;
          final isUnassigned = activeReportId == null;

          return Card(
            child: ListTile(
              onTap: () => _focusOnReport(r),
              title: Text(r.title),
              subtitle: Text(
                "Severity: ${r.severity} • Status: ${r.status}",
              ),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(Icons.navigation),
                    onPressed: onDuty
                        ? () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => NavigationScreen(report: r),
                              ),
                            );
                          }
                        : null,
                  ),
                  IconButton(
                    icon: const Icon(Icons.check),
                    onPressed: onDuty && isMine
                        ? () async {
                            await api.resolveReport(r.id, auth.uid!);

                            final prefs = await SharedPreferences.getInstance();
                            await prefs.remove("activeReportId");
                            activeReportId = null;

                            await _loadReportsInArea();
                          }
                        : null,
                  ),
                  IconButton(
                    icon: const Icon(Icons.assignment),
                    onPressed: onDuty && isUnassigned
                        ? () async {
                            await api.manualAssignReport(r.id);

                            final prefs = await SharedPreferences.getInstance();
                            await prefs.setString("activeReportId", r.id);
                            activeReportId = r.id;

                            await _loadReportsInArea();
                          }
                        : null,
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
  Widget _buildDebugButtons() {
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 8),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        ElevatedButton(
          onPressed: () async {
            if (_userLocation == null) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text("No location available")),
              );
              return;
            }

            print("DEBUG: Calling suggest_for_responder manually...");

            final response = await api.suggestForResponder(
              responderUid: auth.uid!,
              lat: _userLocation!.latitude,
              lng: _userLocation!.longitude,
            );

            print("DEBUG RAW RESPONSE: $response");

            if (response == null || response["suggested"] == null) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text("No suggestion returned")),
              );
              return;
            }

            final reportJson = response["suggested"];
            final report = Report.fromJson(reportJson);

            if (!mounted) return;

            showDialog(
              context: context,
              builder: (_) {
                return AlertDialog(
                  title: const Text("DEBUG: Προτεινόμενο περιστατικό"),
                  content: Text(
                    "ID: ${report.id}\n"
                    "Title: ${report.title}\n"
                    "Severity: ${report.severity}\n"
                    "On hold for: ${reportJson["on_hold_for"]}\n"
                    "Status: ${report.status}",
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text("OK"),
                    ),
                  ],
                );
              },
            );
          },
          child: const Text("DEBUG: Auto‑Suggest"),
        ),
      ],
    ),
  );
}

}
