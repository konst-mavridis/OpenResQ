import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import 'home_screen.dart';
import 'package:fluttertoast/fluttertoast.dart';

class RegisterScreen extends StatelessWidget {
  RegisterScreen({super.key});

  final AuthService auth = AuthService();

  final emailController = TextEditingController();
  final passController = TextEditingController();
  final displayNameController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Register")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(
              controller: emailController,
              decoration: const InputDecoration(labelText: "Email"),
            ),
            TextField(
              controller: passController,
              obscureText: true,
              decoration: const InputDecoration(labelText: "Password"),
            ),
            TextField(
              controller: displayNameController,
              decoration: const InputDecoration(labelText: "Display Name"),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              child: const Text("Create account"),
              onPressed: () async {
                try {
                  await auth.register(
                    emailController.text.trim(),
                    passController.text.trim(),
                  );

                  if (!context.mounted) return;
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (_) => const HomeRouter()),
                  );
                } catch (e) {
                  Fluttertoast.showToast(msg: e.toString());
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}
