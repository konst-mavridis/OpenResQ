import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:openresq_app/services/api_service.dart';
import '../models/report.dart';
import 'dart:math';
import '../services/auth_service.dart';
import '../screens/navigations_screen.dart';
class MarkerPopup extends StatelessWidget {
  final Report report;
  final MapController mapController;
  final VoidCallback onClose;
  final VoidCallback onDetails;
  final auth = AuthService();
  final String? role;

  MarkerPopup({
    super.key,
    required this.report,
    required this.mapController,
    required this.onClose,
    required this.onDetails,
    required this.role,
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


      return Material(
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

              if (role != "citizen" && report.assignedTo == null)
                ElevatedButton.icon(
                  icon: const Icon(Icons.handshake),
                  label: const Text("Assign to me"),
                  onPressed: () async {
                    try {
                      await ApiService().claimReport(report.id);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text("Report assigned to you")),
                      );
                      Navigator.of(context).pushReplacement(
                        MaterialPageRoute(
                          builder: (_) => NavigationScreen(report: report),
                        ),
                      );
                      onClose();
                    } catch (e) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text("Already assigned")),
                      );
                      onClose();

                    }
                  },
                ),

              if (report.assignedTo != null)
                Text(
                  "Assigned to: ${report.assignedTo}",
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ElevatedButton(
                onPressed: onDetails,
                child: const Text("Go to details"),
              ),

              TextButton(
                onPressed: onClose,
                child: const Text("Close"),
              ),
            ],
          ),
        ),
      );

    }
}
