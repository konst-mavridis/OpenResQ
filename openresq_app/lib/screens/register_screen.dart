import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';
import 'otp_screen.dart';

enum UserRole { citizen, responder }

class RegisterScreen extends StatefulWidget {
  final String? inviteToken;
  const RegisterScreen({super.key, this.inviteToken});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final AuthService auth = AuthService();

  final emailController = TextEditingController();
  final passController = TextEditingController();
  final displayNameController = TextEditingController();

  bool loading = false;
  String? emailError;
  String? passError;
  String? nameError;

  UserRole selectedRole = UserRole.citizen;

  @override
  void dispose() {
    emailController.dispose();
    passController.dispose();
    displayNameController.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    setState(() {
      loading = true;
      emailError = null;
      passError = null;
      nameError = null;
    });

    final email = emailController.text.trim();
    final pass = passController.text.trim();
    final name = displayNameController.text.trim();

    if (email.isEmpty) {
      setState(() {
        emailError = "Email is required";
        loading = false;
      });
      return;
    }

    if (!email.contains("@")) {
      setState(() {
        emailError = "Invalid email";
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

    if (name.isEmpty) {
      setState(() {
        nameError = "Display name is required";
        loading = false;
      });
      return;
    }

    try {
      await auth.register(
        email,
        pass,
        displayName: name,
        inviteToken: widget.inviteToken,
        selectedRole: selectedRole == UserRole.responder ? "responder" : "citizen",
      );

      await ApiService().sendOTP(email);

      Fluttertoast.showToast(msg: "Account created! Please verify your email.");

      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => OTPScreen(email: email),
        ),
      );
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
    return Scaffold(
      body: Stack(
        children: [
          Positioned.fill(
            child: Image.asset(
              "assets/login_bg.png",
              fit: BoxFit.cover,
            ),
          ),

          Positioned.fill(
            child: Container(
              color: Colors.black.withOpacity(0.55),
            ),
          ),

          Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 28),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "Create Account",
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),

                  const SizedBox(height: 30),

                  TextField(
                    controller: emailController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      labelText: "Email",
                      labelStyle: const TextStyle(color: Colors.white70),
                      errorText: emailError,
                      filled: true,
                      fillColor: Colors.white.withOpacity(0.15),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  TextField(
                    controller: passController,
                    obscureText: true,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      labelText: "Password",
                      labelStyle: const TextStyle(color: Colors.white70),
                      errorText: passError,
                      filled: true,
                      fillColor: Colors.white.withOpacity(0.15),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  TextField(
                    controller: displayNameController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      labelText: "Display Name",
                      labelStyle: const TextStyle(color: Colors.white70),
                      errorText: nameError,
                      filled: true,
                      fillColor: Colors.white.withOpacity(0.15),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),

                  const SizedBox(height: 28),

                  Text(
                    "Select Role",
                    style: TextStyle(color: Colors.white70, fontSize: 16),
                  ),

                  RadioListTile<UserRole>(
                    value: UserRole.citizen,
                    groupValue: selectedRole,
                    onChanged: (value) {
                      setState(() => selectedRole = value!);
                    },
                    title: const Text("Citizen", style: TextStyle(color: Colors.white)),
                    activeColor: Colors.redAccent,
                  ),

                  RadioListTile<UserRole>(
                    value: UserRole.responder,
                    groupValue: selectedRole,
                    onChanged: (value) {
                      setState(() => selectedRole = value!);
                    },
                    title: const Text("Responder", style: TextStyle(color: Colors.white)),
                    activeColor: Colors.redAccent,
                  ),

                  const SizedBox(height: 28),

                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: loading ? null : _register,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.redAccent,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      child: loading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text(
                              "Create Account",
                              style: TextStyle(fontSize: 18),
                            ),
                    ),
                  ),

                  const SizedBox(height: 20),

                  Center(
                    child: TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text(
                        "Already have an account? Login",
                        style: TextStyle(color: Colors.white70),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
