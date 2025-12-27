import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../models/report.dart';
import 'dart:math';

class MarkerPopup extends StatelessWidget {
  final Report report;
  final MapController mapController;
  final VoidCallback onClose;
  final VoidCallback onDetails;

  const MarkerPopup({
    super.key,
    required this.report,
    required this.mapController,
    required this.onClose,
    required this.onDetails,
  });

  @override
  Widget build(BuildContext context) {
    final projected = mapController.camera.project(
      LatLng(report.latitude, report.longitude),
    );

    final origin = mapController.camera.pixelOrigin;

    final point = projected -
        Point<double>(
          origin.x.toDouble(),
          origin.y.toDouble(),
        );


    return Positioned(
      left: point.x - 100.0,
      top: point.y - 120.0,
      child: Material(
        elevation: 6,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          width: 200,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                report.title,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: onDetails,
                child: const Text("Go to details"),
              ),
              TextButton(
                onPressed: onClose,
                child: const Text("Close"),
              )
            ],
          ),
        ),
      ),
    );
  }
}
