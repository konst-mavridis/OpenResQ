import 'package:flutter/material.dart';

class HazardCard extends StatelessWidget {
  final Map<String, dynamic> hazard;

  const HazardCard({super.key, required this.hazard});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(10),
      child: ListTile(
        title: Text(hazard["title"]),
        subtitle: Text(hazard["description"]),
        trailing: Text(hazard["level"]),
      ),
    );
  }
}
