import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class NearbyTeamsScreen extends StatefulWidget {
  const NearbyTeamsScreen({super.key});

  @override
  State<NearbyTeamsScreen> createState() => _NearbyTeamsScreenState();
}

class _NearbyTeamsScreenState extends State<NearbyTeamsScreen> {
  final api = ApiService();
  final auth = AuthService();

  bool loading = true;
  List<dynamic> teams = [];
  String? error;

  @override
  void initState() {
    super.initState();
    _loadNearbyTeams();
  }

  Future<void> _loadNearbyTeams() async {
    try {
      setState(() {
        loading = true;
        error = null;
      });

      final pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      final response = await api.get("/teams/nearby", params: {
        "lat": pos.latitude,
        "lng": pos.longitude,
        "radius_km": 20,
      });

      setState(() {
        teams = response;
      });
    } catch (e) {
      setState(() => error = e.toString());
    } finally {
      setState(() => loading = false);
    }
  }

  Future<void> _joinTeam(String teamId, String name) async {
    try {
      await api.post("/teams/join_request", {
        "team_id": teamId,
        "responder_uid": auth.uid!,
        "responder_email": auth.email!,
      });

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Join request sent to $name")),
      );

      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Error sending join request: $e")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Nearby Teams (20km)"),
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : error != null
              ? Center(child: Text("Error: $error"))
              : teams.isEmpty
                  ? const Center(
                      child: Text(
                        "No teams found within 20km.",
                        style: TextStyle(fontSize: 16),
                      ),
                    )
                  : ListView.builder(
                      itemCount: teams.length,
                      itemBuilder: (_, i) {
                        final t = teams[i];
                        final name = t["name"] ?? "Unnamed Team";
                        final id = t["id"];

                        return Card(
                          child: ListTile(
                            title: Text(name),
                            subtitle: Text("Team ID: $id"),
                            trailing: ElevatedButton(
                              onPressed: () => _joinTeam(id, name),
                              child: const Text("Join"),
                            ),
                          ),
                        );
                      },
                    ),
    );
  }
}
