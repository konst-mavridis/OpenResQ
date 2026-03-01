import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../services/api_service.dart';
import '../screens/assign_leader_screen.dart';

class TeamsScreen extends StatefulWidget {
  const TeamsScreen({super.key});

  @override
  State<TeamsScreen> createState() => _TeamsScreenState();
}

class _TeamsScreenState extends State<TeamsScreen> {
  final TextEditingController _teamNameController = TextEditingController();


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Teams Management")),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _teamNameController,
                    decoration: const InputDecoration(
                      labelText: "Team Name",
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: () async {
                    if (_teamNameController.text.isNotEmpty) {
                      await ApiService().createTeam(_teamNameController.text);
                      _teamNameController.clear();
                    }
                  },
                  child: const Text("Create"),
                )
              ],
            ),
          ),

          const Divider(),

          Expanded(
            child: StreamBuilder(
              stream: FirebaseFirestore.instance.collection("teams").snapshots(),
              builder: (context, snapshot) {
                if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());

                final teams = snapshot.data!.docs;

                return ListView.builder(
                  itemCount: teams.length,
                  itemBuilder: (context, index) {
                    final team = teams[index];
                    return ListTile(
                      title: Text(team["name"]),

                      subtitle: team["leader_uid"] == null
                          ? const Text("Leader: None")
                          : FutureBuilder<DocumentSnapshot>(
                              future: FirebaseFirestore.instance
                                  .collection("users")
                                  .doc(team["leader_uid"])
                                  .get(),
                              builder: (context, snapshot) {
                                if (!snapshot.hasData) {
                                  return const Text("Leader: Loading...");
                                }

                                final data = snapshot.data!.data() as Map<String, dynamic>?;

                                final leaderName = data?["displayName"]
                                    ?? data?["display_name"]
                                    ?? data?["name"]
                                    ?? data?["email"]
                                    ?? "Unknown User";

                                return Text("Leader: $leaderName");
                              },
                            ),

                      trailing: ElevatedButton(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => AssignLeaderScreen(teamId: team.id),
                            ),
                          );
                        },
                        child: Text(team["leader_uid"] == null ? "Assign Leader" : "Change"),
                      ),
                    );


                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
