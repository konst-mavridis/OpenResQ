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


  String eta = "--";
  String distance = "--";

  double? _lastDistance;

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
          GoogleMap(
            initialCameraPosition: CameraPosition(
              target: _currentPos!,
              zoom: 18,
              tilt: 70,
            ),
            onMapCreated: (c) => _mapController = c,
            myLocationEnabled: true,
            polylines: _polylines,
            markers: {
              Marker(
                markerId: const MarkerId("target"),
                position: LatLng(
                  widget.report.latitude,
                  widget.report.longitude,
                ),
              ),
            },
          ),

          Positioned(
            top: 50,
            left: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.black87,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text("ETA: $eta",
                      style: const TextStyle(color: Colors.white)),
                  Text("DIST: $distance",
                      style: const TextStyle(color: Colors.white)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
