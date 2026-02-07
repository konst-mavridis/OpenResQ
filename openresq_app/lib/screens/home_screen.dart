import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'user_home.dart';
import 'responder_home.dart';
import 'admin_dashboard.dart';

class HomeRouter extends StatefulWidget {
  const HomeRouter({super.key});

  @override
  State<HomeRouter> createState() => _HomeRouterState();
}

class _HomeRouterState extends State<HomeRouter> {
  final api = ApiService();
  final auth = AuthService();

  String? role;
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
    } catch (_) {
      role = "citizen";
    }

    setState(() => loading = false);
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
    return const UserHomePage();
  }
}
