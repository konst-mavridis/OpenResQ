import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'home_screen.dart';
import 'login_screen.dart';
import 'reset_password_screen.dart';
import 'package:app_links/app_links.dart';
import 'register_screen.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  late final AppLinks _appLinks;
  bool _handledInitialLink = false; // prevents double navigation

  @override
  void initState() {
    super.initState();
    _initDeepLinks();
  }

  Future<void> _initDeepLinks() async {
    _appLinks = AppLinks();

    // 1. Handle initial link (app opened from terminated)
    final initial = await _appLinks.getInitialAppLink();
    if (initial != null && !_handledInitialLink) {
      _handledInitialLink = true;
      _handleLink(initial);
    }

    // 2. Handle links while app is running
    _appLinks.uriLinkStream.listen((Uri? link) {
      if (link != null) {
        _handleLink(link);
      }
    });
  }

  void _handleLink(Uri link) {
    if (!mounted) return;

    if (link.path == "/reset-password") {
      final token = link.queryParameters["token"];
      if (token != null) {
        // Delay navigation to avoid "setState during build" crash
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (!mounted) return;
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ResetPasswordScreen(token: token),
            ),
          );
        });
      }
    }

    if (link.host == "openresq.pages.dev" && link.path == "/invite") {
      final token = link.queryParameters["token"];
      if (token != null) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => RegisterScreen(inviteToken: token),
            ),
          );
        });
      }
    }


  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        // Loading state
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        // Logged in
        if (snapshot.hasData) {
          return const HomeRouter();
        }

        // Logged out
        return const LoginScreen();
      },
    );
  }
}
