import 'package:flutter/material.dart';

class ReportCard extends StatelessWidget {
  final Map<String, dynamic> report;

  const ReportCard({super.key, required this.report});

  @override
  Widget build(BuildContext context) {
    final title = report["title"]?.toString() ?? "Untitled";
    final description = report["description"]?.toString() ?? "No description";
    final status = report["status"]?.toString() ?? "Pending";
    
    return Card(
      margin: const EdgeInsets.all(10),
      child: ListTile(
        title: Text(title),
        subtitle: Text(description),
        trailing: Text(status),
      ),
    );
  }
}
