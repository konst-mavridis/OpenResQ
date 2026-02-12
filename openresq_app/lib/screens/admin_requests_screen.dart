import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class AdminResponderRequestsScreen extends StatelessWidget {
  const AdminResponderRequestsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Responder Requests"),
        backgroundColor: Colors.redAccent,
      ),
      body: StreamBuilder(
        stream: FirebaseFirestore.instance
            .collection("responder_requests")
            .where("status", isEqualTo: "pending")
            .snapshots(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }

          final docs = snapshot.data!.docs;

          if (docs.isEmpty) {
            return const Center(
              child: Text(
                "No pending requests",
                style: TextStyle(fontSize: 18),
              ),
            );
          }

          return ListView.builder(
            itemCount: docs.length,
            itemBuilder: (context, i) {
              final data = docs[i].data();
              final userId = data["userId"];
              final email = data["email"];
              final name = data["displayName"];

              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: ListTile(
                  title: Text(name),
                  subtitle: Text(email),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.check, color: Colors.green),
                        onPressed: () async {
                          // Approve
                          await FirebaseFirestore.instance
                              .collection("users")
                              .doc(userId)
                              .update({"role": "responder"});

                          await FirebaseFirestore.instance
                              .collection("responder_requests")
                              .doc(userId)
                              .update({"status": "approved"});
                        },
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.red),
                        onPressed: () async {
                          // Reject
                          await FirebaseFirestore.instance
                              .collection("responder_requests")
                              .doc(userId)
                              .update({"status": "rejected"});
                        },
                      ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
