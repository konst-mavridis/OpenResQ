import 'dart:async';
import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import '../services/api_service.dart';

class OTPScreen extends StatefulWidget {
  final String email;
  const OTPScreen({super.key, required this.email});

  @override
  State<OTPScreen> createState() => _OTPScreenState();
}

class _OTPScreenState extends State<OTPScreen> {
  final ApiService api = ApiService();
  final otpController = TextEditingController();

  bool loading = false;
  bool blocked = false;
  int secondsLeft = 60;
  Timer? timer;

  @override
  void initState() {
    super.initState();
    startTimer();
    otpController.addListener(_autoSubmit);
  }

  @override
  void dispose() {
    timer?.cancel();
    otpController.dispose();
    super.dispose();
  }

  void startTimer() {
    secondsLeft = 60;
    timer?.cancel();
    timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (secondsLeft == 0) {
        t.cancel();
      } else {
        setState(() => secondsLeft--);
      }
    });
  }

  void _autoSubmit() {
    if (otpController.text.length == 6) {
      verify();
    }
  }

  Future<void> verify() async {
    if (blocked) return;

    setState(() => loading = true);

    try {
      await api.verifyOTP(widget.email, otpController.text.trim());
      Fluttertoast.showToast(msg: "Email verified!");

      if (!mounted) return;
      Navigator.pop(context);
    } catch (e) {
      final msg = e.toString();

      if (msg.contains("Too many attempts")) {
        setState(() => blocked = true);
      }

      Fluttertoast.showToast(msg: msg);
    } finally {
      setState(() => loading = false);
    }
  }

  Future<void> resend() async {
    if (secondsLeft > 0) return;

    try {
      await api.resendOTP(widget.email);
      Fluttertoast.showToast(msg: "OTP sent again");
      startTimer();
    } catch (e) {
      Fluttertoast.showToast(msg: e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Background image (same as Login/Register)
          Positioned.fill(
            child: Image.asset(
              "assets/login_bg.png",
              fit: BoxFit.cover,
            ),
          ),

          // Dark overlay
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
                    "Verify Email",
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),

                  const SizedBox(height: 20),

                  Text(
                    "Enter the 6‑digit code sent to ${widget.email}",
                    style: const TextStyle(color: Colors.white70),
                  ),

                  const SizedBox(height: 20),

                  TextField(
                    controller: otpController,
                    keyboardType: TextInputType.number,
                    maxLength: 6,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      labelText: "OTP Code",
                      labelStyle: const TextStyle(color: Colors.white70),
                      filled: true,
                      fillColor: Colors.white.withOpacity(0.15),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),

                  const SizedBox(height: 20),

                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: loading ? null : verify,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.redAccent,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      child: loading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text("Verify", style: TextStyle(fontSize: 18)),
                    ),
                  ),

                  const SizedBox(height: 20),

                  Center(
                    child: Text(
                      secondsLeft > 0
                          ? "Resend available in $secondsLeft seconds"
                          : "You can resend now",
                      style: const TextStyle(color: Colors.white70),
                    ),
                  ),

                  Center(
                    child: TextButton(
                      onPressed: secondsLeft == 0 ? resend : null,
                      child: const Text(
                        "Resend OTP",
                        style: TextStyle(color: Colors.white),
                      ),
                    ),
                  ),

                  if (blocked)
                    const Center(
                      child: Text(
                        "Too many wrong attempts. Try again later.",
                        style: TextStyle(color: Colors.redAccent),
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
