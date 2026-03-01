import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'user_home.dart';
import 'responder_home.dart';
import 'admin_dashboard.dart';
import 'team_leader_dashboard.dart';
import '../services/location_service.dart'; 
import 'package:cloud_firestore/cloud_firestore.dart';
class HomeRouter extends StatefulWidget {
  const HomeRouter({super.key});

  @override
  State<HomeRouter> createState() => _HomeRouterState();
}

class _HomeRouterState extends State<HomeRouter> {
  final api = ApiService();
  final auth = AuthService();

  String? role;
  String? teamId;
  String? teamName;
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _loadRole();
  }

  Future<void> _loadRole() async {
    try {
      final me = await api.getMe();
      role = me["role"];
      teamId = me["team_id"];   // <-- μπορεί να είναι null, και αυτό είναι ΟΚ
      if (role == "team_leader" && teamId != null && teamId!.isNotEmpty) {
        teamName = await getTeamNameFromId(teamId!);
      }
    } catch (_) {
      role = "citizen";
    }

    setState(() => loading = false);
  }


  Future<String?> getTeamNameFromId(String teamId) async {
    final doc = await FirebaseFirestore.instance
        .collection("teams")
        .doc(teamId)
        .get();

    if (!doc.exists) return null;

    return doc.data()?["name"];
  }


  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (role == "admin") return const AdminDashboardPage();
    if (role == "responder") return const ResponderHomePage();

    if (role == "responder" || role == "team_leader") {
      LocationService.startLiveLocationUpdates();
    }

    if (role == "team_leader") {
      if (teamId == null || teamId!.isEmpty) {
        return const Scaffold(
          body: Center(
            child: Text(
              "Error: This team leader has no team assigned.",
              style: TextStyle(fontSize: 18),
            ),
          ),
        );
      }
      return TeamLeaderDashboard(
        teamId: teamId!,
        leaderUid: auth.currentUser!.uid,
        name: teamName ?? "Unknown Team",
      );
    }

    return const UserHomePage();
  }
}
