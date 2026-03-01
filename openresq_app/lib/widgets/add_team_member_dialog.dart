import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class AddTeamMemberDialog extends StatefulWidget {
  final String teamId;

  const AddTeamMemberDialog({super.key, required this.teamId});

  @override
  State<AddTeamMemberDialog> createState() => _AddTeamMemberDialogState();
}

class _AddTeamMemberDialogState extends State<AddTeamMemberDialog> {
  final TextEditingController emailController = TextEditingController();
  bool loading = false;
  String? error;

  Future<void> addMember() async {
    setState(() {
      loading = true;
      error = null;
    });

    try {
      final email = emailController.text.trim();

      if (email.isEmpty) {
        setState(() => error = "Please enter an email.");
        return;
      }

      // Find user by email
      final query = await FirebaseFirestore.instance
          .collection("users")
          .where("email", isEqualTo: email)
          .limit(1)
          .get();

      if (query.docs.isEmpty) {
        setState(() => error = "No user found with this email.");
        return;
      }

      final userDoc = query.docs.first;

      // Assign team_id
      await FirebaseFirestore.instance
          .collection("users")
          .doc(userDoc.id)
          .update({"team_id": widget.teamId});

      if (!mounted) return;
      Navigator.pop(context);
    } catch (e) {
      setState(() => error = e.toString());
    } finally {
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text("Add Team Member"),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: emailController,
            decoration: const InputDecoration(
              labelText: "User Email",
            ),
          ),
          if (error != null)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                error!,
                style: const TextStyle(color: Colors.red),
              ),
            ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: loading ? null : () => Navigator.pop(context),
          child: const Text("Cancel"),
        ),
        ElevatedButton(
          onPressed: loading ? null : addMember,
          child: loading
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text("Add"),
        ),
      ],
    );
  }
}
