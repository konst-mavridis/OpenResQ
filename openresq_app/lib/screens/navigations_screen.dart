import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:flutter_polyline_points/flutter_polyline_points.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../models/report.dart';
import '../services/tts_service.dart';
import '../services/api_service.dart';
import '../screens/home_screen.dart';
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
  final ApiService api = ApiService();

  final Set<Polyline> _polylines = {};
  final FlutterTts tts = FlutterTts();

  bool _isSpeakingEnabled = true;
  bool _isNavigating = true;
  bool _hasArrived = false;

  void _onMapCreated(GoogleMapController controller) {
    _mapController = controller;
  }

  String eta = "--";
  String distance = "--";
  String speed = "0 km/h";

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
    try {
      final pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.bestForNavigation,
      );

      _currentPos = LatLng(pos.latitude, pos.longitude);
      await _drawRoute();
      _startTracking();
      setState(() {});
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error getting location: $e')),
        );
      }
    }
  }

  /// 🔵 DRAW ROUTE
  Future<void> _drawRoute() async {
    try {
      if (_currentPos == null) return;
      
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

        if (mounted) {
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
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error drawing route: $e')),
        );
      }
    }
  }

  void _updateNavigation(Position pos) {
    if (_routePoints.isEmpty || _currentRouteIndex >= _routePoints.length - 1) {
      if (!_hasArrived) {
        _hasArrived = true;
        _speakText("You have arrived at your destination");
      }
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
      _speakText("$instruction in 50 meters");
      _lastSpokenMeter = 50;
    }

    if ((distance ~/ 5) != _lastSpokenMeter) {
      _lastSpokenMeter = distance ~/ 5;
      if (mounted) setState(() {});
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
    final speedKmh = (pos.speed * 3.6).toStringAsFixed(1);

    if (mounted) {
      setState(() {
        distance = "${(meters / 1000).toStringAsFixed(2)} km";
        eta = "${(seconds / 60).toStringAsFixed(0)} min";
        this.speed = "$speedKmh km/h";
      });
    }

    // Speak updates every 200 meters
    if ((_lastDistance ?? 0) - meters > 200) {
      _speakText("Estimated time of arrival is $eta");
    }

    if (meters < 50 && !_hasArrived) {
      _speakText("You have arrived at your destination");
    }
  }

  void _checkReRoute(double currentDistance) {
    if (_lastDistance != null && currentDistance > _lastDistance! + 30) {
      _drawRoute();
      _speakText("Recalculating route");
    }
    _lastDistance = currentDistance;
  }

  void _speakText(String text) {
    if (_isSpeakingEnabled) {
      speak(text).catchError((e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('TTS Error: $e')),
          );
        }
      });
    }
  }

  Future<void> _exitNavigation() async {
    _isNavigating = false;
    _positionStream?.cancel();
    await tts.stop();

    if (!mounted) return;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Exit Navigation'),
        content: const Text('Do you want to de-assign this report before leaving?'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(dialogContext);
              if (mounted) {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const HomeScreen()),
                  (route) => false,
                );
              }
            },
            child: const Text('Keep Assignment'),
          ),
          FilledButton(
            onPressed: () async {
              Navigator.pop(dialogContext);
              try {
                await api.responderUpdate(widget.report.id, {'status': 'pending'});
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Report de-assigned')),
                  );
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error: $e')),
                  );
                }
              }
              if (mounted) {
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const HomeScreen()),
                  (route) => false,
                );
              }
            },
            child: const Text('De-assign Report'),
          ),
        ],
      ),
    );
  }

  /// 🚗 LIVE NAVIGATION
  void _startTracking() {
    if (!_isNavigating) return;
    
    _positionStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.bestForNavigation,
        distanceFilter: 5,
      ),
    ).listen((pos) {
      _currentPos = LatLng(pos.latitude, pos.longitude);

      _updateEtaAndDistance(pos);
      _updateNavigation(pos);

      if (mounted) {
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
      }
    });
  }

  @override
  void dispose() {
    _isNavigating = false;
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

    return WillPopScope(
      onWillPop: () async {
        _exitNavigation();
        return false;
      },
      child: Scaffold(
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
              markers: const {},
            ),

            /// 🔴 EXIT BUTTON - TOP LEFT
            Positioned(
              top: 40,
              left: 16,
              child: Material(
                elevation: 8,
                borderRadius: BorderRadius.circular(12),
                child: FloatingActionButton(
                  onPressed: _exitNavigation,
                  backgroundColor: Colors.red,
                  mini: true,
                  child: const Icon(Icons.close),
                ),
              ),
            ),

            /// 🔊 VOICE TOGGLE - TOP RIGHT
            Positioned(
              top: 40,
              right: 16,
              child: Material(
                elevation: 8,
                borderRadius: BorderRadius.circular(12),
                child: FloatingActionButton(
                  onPressed: () {
                    setState(() => _isSpeakingEnabled = !_isSpeakingEnabled);
                    _speakText(_isSpeakingEnabled ? "Voice enabled" : "Voice disabled");
                  },
                  backgroundColor: _isSpeakingEnabled ? Colors.blue : Colors.grey,
                  mini: true,
                  child: Icon(_isSpeakingEnabled ? Icons.volume_up : Icons.volume_off),
                ),
              ),
            ),

            /// 🔼 TOP POPUP – TURN INSTRUCTION
            Positioned(
              top: 110,
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

            /// 🔽 BOTTOM POPUP – ETA & DISTANCE & SPEED
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
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _InfoTile(
                            icon: Icons.timer,
                            label: "ETA",
                            value: eta,
                          ),
                          _InfoTile(
                            icon: Icons.route,
                            label: "Distance",
                            value: distance,
                          ),
                          _InfoTile(
                            icon: Icons.speed,
                            label: "Speed",
                            value: speed,
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      if (_hasArrived)
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.green.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.check_circle, color: Colors.green),
                              SizedBox(width: 8),
                              Text(
                                "You have arrived!",
                                style: TextStyle(
                                  color: Colors.green,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),
          
          ],
        ),
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
    return Expanded(
      child: Row(
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
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
