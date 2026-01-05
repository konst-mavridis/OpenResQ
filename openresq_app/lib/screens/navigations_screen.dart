import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:flutter_polyline_points/flutter_polyline_points.dart';
import '../models/report.dart';

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

  @override
  void initState() {
    super.initState();
    _startNavigation();
  }

  Future<void> _startNavigation() async {
    final pos = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.bestForNavigation,
    );

    _currentPos = LatLng(pos.latitude, pos.longitude);
    await _drawRoute();
    _startLiveTracking();

    setState(() {});
  }

  /// 🔵 DRAW BLUE ROUTE
  Future<void> _drawRoute() async {
    final polylinePoints = PolylinePoints();

    final result = await polylinePoints.getRouteBetweenCoordinates(
      googleApiKey: "AIzaSyBHq6f_CM3XSUOFxIzJNbH4V5u_xgJxrBs",
      request: PolylineRequest(
        origin: PointLatLng(_currentPos!.latitude, _currentPos!.longitude),
        destination: PointLatLng(
          widget.report.latitude,
          widget.report.longitude,
        ),
        mode: TravelMode.driving,
      ),
    );

    if (result.points.isNotEmpty) {
      final route = result.points
          .map((p) => LatLng(p.latitude, p.longitude))
          .toList();

      _polylines.clear();
      _polylines.add(
        Polyline(
          polylineId: const PolylineId("route"),
          points: route,
          width: 8,
          color: Colors.blue, // 🔵
          jointType: JointType.round,
          startCap: Cap.roundCap,
          endCap: Cap.roundCap,
        ),
      );
    }
  }

  /// 🚗 LIVE CAMERA FOLLOW (DRIVING MODE)
  void _startLiveTracking() {
    _positionStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.bestForNavigation,
        distanceFilter: 3,
      ),
    ).listen((pos) {
      _currentPos = LatLng(pos.latitude, pos.longitude);

      _mapController?.animateCamera(
        CameraUpdate.newCameraPosition(
          CameraPosition(
            target: _currentPos!,
            zoom: 19,
            tilt: 70,                 // 🔥 driving feel
            bearing: pos.heading,     // 🔥 direction
          ),
        ),
      );
    });
  }

  void _onMapCreated(GoogleMapController controller) {
    _mapController = controller;
  }

  @override
  void dispose() {
    _positionStream?.cancel();
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
      body: GoogleMap(
        initialCameraPosition: CameraPosition(
          target: _currentPos!,
          zoom: 18,
          tilt: 70,
        ),
        onMapCreated: _onMapCreated,
        myLocationEnabled: true,
        myLocationButtonEnabled: false,
        polylines: _polylines,
        markers: {
          Marker(
            markerId: const MarkerId("target"),
            position: LatLng(
              widget.report.latitude,
              widget.report.longitude,
            ),
            infoWindow: const InfoWindow(title: "Incident"),
          ),
        },
      ),
    );
  }
}
