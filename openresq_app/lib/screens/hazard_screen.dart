import 'package:flutter/material.dart';

class HazardScreen extends StatelessWidget {
  const HazardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Hazard Alerts")),
      body: const Center(
        child: Text("Hazards will appear here soon."),
      ),
    );
  }
}
