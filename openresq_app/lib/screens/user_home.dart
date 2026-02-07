import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../models/report.dart';
import '../widgets/report_form.dart';
import 'package:geolocator/geolocator.dart';
import 'dart:async';

class UserHomePage extends StatefulWidget {
  const UserHomePage({super.key});

  @override
  State<UserHomePage> createState() => _UserHomePageState();
}

class _UserHomePageState extends State<UserHomePage> {
  final api = ApiService();
  final auth = AuthService();

  List<Report> reports = [];
  List<Report> filteredReports = [];

  LatLng? _userLocation;
  StreamSubscription<Position>? _positionStream;

  String? severityFilter;
  final bool _followUser = true;
  bool _initialLocationCentered = false;

  final MapController _mapController = MapController();

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    await _goToUserLocation();
    _startLiveLocation();
    await _loadReports();
  }

  Future<void> _loadReports() async {
    try {
      final fetched = await api.getNearbyReports();
      setState(() {
        reports = fetched.map((e) => Report.fromJson(e)).toList();
        filteredReports = reports;
      });
      _autoZoom();
    } catch (e) {
      debugPrint("Error loading reports: $e");
    }
  }

  Future<void> _goToUserLocation() async {
    final pos = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );

    final latLng = LatLng(pos.latitude, pos.longitude);

    setState(() => _userLocation = latLng);

    _mapController.move(latLng, 14.5);

    await api.updateMyArea(
      latitude: pos.latitude,
      longitude: pos.longitude,
      radiusKm: 25,
    );
  }

  void _startLiveLocation() {
    _positionStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.best,
        distanceFilter: 5,
      ),
    ).listen((pos) {
      final latLng = LatLng(pos.latitude, pos.longitude);

    setState(() {
      _userLocation = latLng;
    });

      if (!_initialLocationCentered) {
        _initialLocationCentered = true;
        _autoZoom();
      }

      if (_followUser) {
        _mapController.move(latLng, _mapController.camera.zoom);
      }
    });
  }

  @override
  void dispose() {
    _positionStream?.cancel();
    super.dispose();
  }

  // ================= AUTO-ZOOM =================

  LatLngBounds _calculateBounds() {
    final points = <LatLng>[];

    if (_userLocation != null) {
      points.add(_userLocation!);
    }

    for (final r in filteredReports) {
      points.add(LatLng(r.latitude, r.longitude));
    }

    if (points.isEmpty) {
      return LatLngBounds.fromPoints([LatLng(37.9838, 23.7275)]);
    }

    if (points.length == 1) {
      final p = points.first;
      return LatLngBounds.fromPoints([
        LatLng(p.latitude + 0.0001, p.longitude + 0.0001),
        LatLng(p.latitude - 0.0001, p.longitude - 0.0001),
      ]);
    }

    return LatLngBounds.fromPoints(points);
  }

  void _autoZoom() {
    if (_userLocation == null && filteredReports.isEmpty) return;

    final bounds = _calculateBounds();

    if (bounds.north.isNaN ||
        bounds.south.isNaN ||
        bounds.east.isNaN ||
        bounds.west.isNaN) {
      return;
    }

    if (bounds.north == bounds.south && bounds.east == bounds.west) {
      _mapController.move(bounds.center, 15);
      return;
    }

    _mapController.fitCamera(
      CameraFit.bounds(
        bounds: bounds,
        padding: const EdgeInsets.all(50),
      ),
    );
  }

  // ================= UI =================

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("OpenResQ — Citizen"),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await showModalBottomSheet<bool>(
            context: context,
            isScrollControlled: true,
            builder: (_) => const ReportForm(),
          );
          if (result == true) await _loadReports();
        },
        child: const Icon(Icons.add),
      ),
      body: Column(
        children: [
          _buildFilter(),
          _buildMap(),
          Expanded(child: _buildReportList()),
        ],
      ),
    );
  }

  Widget _buildFilter() {
    return Padding(
      padding: const EdgeInsets.all(8),
      child: DropdownButton<String>(
        value: severityFilter ?? "All",
        items: const [
          DropdownMenuItem(value: "All", child: Text("All severities")),
          DropdownMenuItem(value: "low", child: Text("Low")),
          DropdownMenuItem(value: "medium", child: Text("Medium")),
          DropdownMenuItem(value: "high", child: Text("High")),
        ],
        onChanged: (value) {
          setState(() {
            severityFilter = value;
            filteredReports = value == "All"
                ? reports
                : reports.where((r) => r.severity == value).toList();
          });
          _autoZoom();
        },
      ),
    );
  }

  Widget _buildMap() {
    return SizedBox(
      height: 300,
      child: FlutterMap(
        mapController: _mapController,
        options: MapOptions(
          initialCenter: _userLocation ?? LatLng(37.9838, 23.7275),
          initialZoom: 12,
        ),
        children: [
          TileLayer(
            urlTemplate: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            userAgentPackageName: 'com.openresq.app',
          ),
          MarkerLayer(
            markers: [
              ...filteredReports.map(
                (r) => Marker(
                  point: LatLng(r.latitude, r.longitude),
                  width: 40,
                  height: 40,
                  child: const Icon(
                    Icons.location_on,
                    color: Colors.red,
                    size: 40,
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

  Widget _buildReportList() {
    return ListView.builder(
      itemCount: filteredReports.length,
      itemBuilder: (_, i) {
        final r = filteredReports[i];
        return ListTile(
          title: Text(r.title),
          subtitle: Text("${r.eventType} • ${r.severity}"),
        );
      },
    );
  }
}
