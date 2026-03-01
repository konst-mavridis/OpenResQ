import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../services/api_service.dart';

class AssignLeaderScreen extends StatelessWidget {
  final String teamId;

  const AssignLeaderScreen({super.key, required this.teamId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Assign Team Leader")),
      body: StreamBuilder(
        stream: FirebaseFirestore.instance
            .collection("users")
            .where("role", isEqualTo: "responder")
            .snapshots(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());

          final responders = snapshot.data!.docs;

          return ListView.builder(
            itemCount: responders.length,
            itemBuilder: (context, index) {
              final user = responders[index];
              final data = user.data();

              // SAFE NAME EXTRACTION 
              final name = data["displayName"] ?? data["display_name"] ?? data["name"] ?? data["email"] ?? "Unknown User";

              return ListTile(
                title: Text(name),
                subtitle: Text("UID: ${user.id}"),
                trailing: ElevatedButton(
                  onPressed: () async {
                    await ApiService().assignLeader(teamId, user.id);
                    Navigator.pop(context);
                  },
                  child: const Text("Set Leader"),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
