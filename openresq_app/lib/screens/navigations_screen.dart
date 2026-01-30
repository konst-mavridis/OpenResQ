import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:flutter_polyline_points/flutter_polyline_points.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../models/report.dart';
import '../services/tts_service.dart';
class NavigationScreen extends StatefulWidget {
  final Report report;
  const NavigationScreen({super.key, required this.report});

  @override
  State<NavigationScreen> createState() => _NavigationScreenState();
}

class _NavigationScreenState extends State<NavigationScreen> {
  GoogleMapController? _mapController;
  LatLng? _currentPos;
  StreamSubscription<Position>? _positionStream;

  final Set<Polyline> _polylines = {};

  final FlutterTts tts = FlutterTts();

  void _onMapCreated(GoogleMapController controller) {
    _mapController = controller;
  }

  String eta = "--";
  String distance = "--";

  double? _lastDistance;

  String instruction = "Starting navigation";
  double nextTurnDistance = 0;
  int _lastSpokenMeter = 9999;

  List<LatLng> _routePoints = [];
  int _currentRouteIndex = 0;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    final pos = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.bestForNavigation,
    );

    _currentPos = LatLng(pos.latitude, pos.longitude);
    await _drawRoute();
    _startTracking();
    setState(() {});
  }

    /// 🔵 DRAW ROUTE
  Future<void> _drawRoute() async {
    final polylinePoints = PolylinePoints();

    final result = await polylinePoints.getRouteBetweenCoordinates(
      request: PolylineRequest(
        origin: PointLatLng(
          _currentPos!.latitude,
          _currentPos!.longitude,
        ),
        destination: PointLatLng(
          widget.report.latitude,
          widget.report.longitude,
        ),
        mode: TravelMode.driving,
      ),
      googleApiKey: "AIzaSyBHq6f_CM3XSUOFxIzJNbH4V5u_xgJxrBs",
    );

    if (result.points.isNotEmpty) {
      final route = result.points
          .map((p) => LatLng(p.latitude, p.longitude))
          .toList();
      
      _routePoints = route;

      setState(() {
        _polylines
          ..clear()
          ..add(
            Polyline(
              polylineId: const PolylineId("route"),
              points: route,
              width: 8,
              color: Colors.blue,
            ),
          );
      });
    }
  }

  void _updateNavigation(Position pos) {
    if (_routePoints.isEmpty || _currentRouteIndex >= _routePoints.length - 1) {
      instruction = "You have arrived at your destination";
      return;
    }

    final current = LatLng(pos.latitude, pos.longitude);
    final nextPoint = _routePoints[_currentRouteIndex + 1];

    final distance = Geolocator.distanceBetween(
      current.latitude,
      current.longitude,
      nextPoint.latitude,
      nextPoint.longitude,
    );

    nextTurnDistance = distance;

    if (distance < 5) {
      _currentRouteIndex++;
    }

    final bearingDiff = (pos.heading -
          Geolocator.bearingBetween(
            current.latitude,
            current.longitude,
            nextPoint.latitude,
            nextPoint.longitude,
          )).abs();

    if (bearingDiff > 30 && bearingDiff < 150) {
      instruction = "Turn right ${(bearingDiff).round()} degrees";
    } else if (bearingDiff >= 150) {
      instruction = "Turn left ${(180 - bearingDiff).round()} degrees";
    } else {
      instruction = "Continue straight";
    }

    if (distance <= 50 && _lastSpokenMeter - distance > 50) {
      speak("$instruction in 50 meters");
      _lastSpokenMeter = 50;
    }

    if ((distance ~/ 5) != _lastSpokenMeter) {
      _lastSpokenMeter = distance ~/ 5;
      setState(() {});
    }
  }

  /// ⏱️ UPDATE ETA & DISTANCE
  void _updateEtaAndDistance(Position pos) {
    final meters = Geolocator.distanceBetween(
      pos.latitude,
      pos.longitude,
      widget.report.latitude,
      widget.report.longitude,
    );

    _checkReRoute(meters);

    final speed = pos.speed > 1 ? pos.speed : 13.8; // m/s (13.8 m/s = 50 km/h)
    final seconds = meters / speed;

    setState(() {
      distance = "${(meters / 1000).toStringAsFixed(2)} km";
      eta = "${(seconds / 60).toStringAsFixed(0)} min";
      speak("Estimated time of arrival is $eta");
      speak("Distance to destination is $distance");
      if (meters < 50) {
        speak("You have arrived at your destination");
      }
    });
  }

  void _checkReRoute(double currentDistance) {
    if (_lastDistance != null && currentDistance > _lastDistance! + 30) {
      _drawRoute();
      speak("Recalculating route");
    }
    _lastDistance = currentDistance;
  }
  /// 🚗 LIVE NAVIGATION
  void _startTracking() {
    _positionStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.bestForNavigation,
        distanceFilter: 5,
      ),
    ).listen((pos) {
      _currentPos = LatLng(pos.latitude, pos.longitude);

      _updateEtaAndDistance(pos);
      _updateNavigation(pos);

      speak("You are $distance away, estimated time of arrival is $eta");
      _mapController?.animateCamera(
        CameraUpdate.newCameraPosition(
          CameraPosition(
            target: _currentPos!,
            zoom: 19,
            tilt: 70,
            bearing: pos.heading,
          ),
        ),
      );
    });
  }

  @override
  void dispose() {
    _positionStream?.cancel();
    tts.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_currentPos == null) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      body: Stack(
        children: [
          /// 🗺 MAP
          GoogleMap(
            initialCameraPosition: CameraPosition(
              target: _currentPos!,
              zoom: 18,
              tilt: 70,
            ),
            onMapCreated: _onMapCreated,
            myLocationEnabled: true,
            myLocationButtonEnabled: false,
            polylines: _polylines,
          ),

          /// 🔼 TOP POPUP – TURN INSTRUCTION
          Positioned(
            top: 40,
            left: 16,
            right: 16,
            child: Material(
              elevation: 8,
              borderRadius: BorderRadius.circular(14),
              child: Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.navigation, size: 32, color: Colors.blue),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            instruction,
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            "Σε ${nextTurnDistance.toStringAsFixed(0)} μ",
                            style: const TextStyle(fontSize: 14),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          /// 🔽 BOTTOM POPUP – ETA & DISTANCE
          Positioned(
            bottom: 24,
            left: 16,
            right: 16,
            child: Material(
              elevation: 8,
              borderRadius: BorderRadius.circular(16),
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 14,
                ),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _InfoTile(
                      icon: Icons.timer,
                      label: "ETA",
                      value: eta ?? "--",
                    ),
                    _InfoTile(
                      icon: Icons.route,
                      label: "Distance",
                      value: distance ?? "--",
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}



class _InfoTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoTile({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, color: Colors.blue),
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
            Text(
              value,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
