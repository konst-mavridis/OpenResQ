import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import '../services/api_service.dart';

class ResetPasswordScreen extends StatefulWidget {
  final String token;

  const ResetPasswordScreen({super.key, required this.token});

  @override
  State<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends State<ResetPasswordScreen> {
  final ApiService api = ApiService();

  final TextEditingController passController = TextEditingController();
  final TextEditingController confirmController = TextEditingController();

  bool loading = false;
  String? passError;
  String? confirmError;

  @override
  void dispose() {
    passController.dispose();
    confirmController.dispose();
    super.dispose();
  }

  Future<void> _resetPassword() async {
    setState(() {
      loading = true;
      passError = null;
      confirmError = null;
    });

    final pass = passController.text.trim();
    final confirm = confirmController.text.trim();

    if (pass.isEmpty) {
      setState(() {
        passError = "Password is required";
        loading = false;
      });
      return;
    }

    if (pass.length < 6) {
      setState(() {
        passError = "Password must be at least 6 characters";
        loading = false;
      });
      return;
    }

    if (confirm != pass) {
      setState(() {
        confirmError = "Passwords do not match";
        loading = false;
      });
      return;
    }

    try {
      await api.resetPassword(widget.token, pass);

      Fluttertoast.showToast(msg: "Password updated successfully");

      if (!mounted) return;

      Navigator.pop(context); // back to login
    } catch (e) {
      Fluttertoast.showToast(msg: e.toString());
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text("Reset Password")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(
              controller: passController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: "New Password",
                errorText: passError,
                prefixIcon: const Icon(Icons.lock_outline),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: confirmController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: "Confirm Password",
                errorText: confirmError,
                prefixIcon: const Icon(Icons.lock_outline),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: loading ? null : _resetPassword,
                style: ElevatedButton.styleFrom(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: loading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text("Reset Password"),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
