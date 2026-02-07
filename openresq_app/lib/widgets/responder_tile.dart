import 'package:flutter/material.dart';

class ResponderTile extends StatelessWidget {
  final Map<String, dynamic> responder;
  final VoidCallback onRemove;

  const ResponderTile({required this.responder, required this.onRemove, super.key});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(responder['display_name'] ?? responder['name'] ?? 'Unknown'),
      subtitle: Text(responder['role'] ?? 'responder'),
      trailing: IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: onRemove),
    );
  }
}
