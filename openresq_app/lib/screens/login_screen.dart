import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:local_auth/local_auth.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:fluttertoast/fluttertoast.dart';

import '../services/auth_service.dart';
import 'home_screen.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen>
    with SingleTickerProviderStateMixin {
  final AuthService auth = AuthService();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passController = TextEditingController();

  bool loading = false;
  bool obscure = true;
  bool rememberMe = false;

  String? emailError;
  String? passError;
  String? generalError;

  late AnimationController _animController;
  late Animation<double> _fadeAnim;
  late Animation<Offset> _slideAnim;

  final LocalAuthentication _localAuth = LocalAuthentication();
  bool canCheckBiometrics = false;

  @override
  void initState() {
    super.initState();
    _initAnimations();
    _loadRememberedEmail();
    _checkBiometrics();
  }

  void _initAnimations() {
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    );

    _fadeAnim = CurvedAnimation(
      parent: _animController,
      curve: Curves.easeIn,
    );

    _slideAnim = Tween<Offset>(
      begin: const Offset(0, 0.2),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _animController,
        curve: Curves.easeOut,
      ),
    );

    _animController.forward();
  }

  Future<void> _loadRememberedEmail() async {
    final prefs = await SharedPreferences.getInstance();
    final savedEmail = prefs.getString('remembered_email');
    if (savedEmail != null && savedEmail.isNotEmpty) {
      setState(() {
        emailController.text = savedEmail;
        rememberMe = true;
      });
    }
  }

  Future<void> _checkBiometrics() async {
    try {
      final canCheck = await _localAuth.canCheckBiometrics;
      final isDeviceSupported = await _localAuth.isDeviceSupported();
      setState(() {
        canCheckBiometrics = canCheck && isDeviceSupported;
      });
    } on PlatformException {
      setState(() {
        canCheckBiometrics = false;
      });
    }
  }

  @override
  void dispose() {
    emailController.dispose();
    passController.dispose();
    _animController.dispose();
    super.dispose();
  }

  Future<void> _onLogin() async {
    setState(() {
      loading = true;
      emailError = null;
      passError = null;
      generalError = null;
    });

    final email = emailController.text.trim();
    final pass = passController.text.trim();

    if (email.isEmpty) {
      setState(() {
        emailError = "Email is required";
        loading = false;
      });
      return;
    }
    if (pass.isEmpty) {
      setState(() {
        passError = "Password is required";
        loading = false;
      });
      return;
    }

    try {
      await auth.login(email, pass);

      final prefs = await SharedPreferences.getInstance();
      if (rememberMe) {
        await prefs.setString('remembered_email', email);
      } else {
        await prefs.remove('remembered_email');
      }

      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const HomeRouter()),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        generalError = e.toString();
      });
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  Future<void> _onBiometricLogin() async {
    try {
      final didAuth = await _localAuth.authenticate(
        localizedReason: 'Login with biometrics',
        biometricOnly: true,
      );

      if (!didAuth) return;

      Fluttertoast.showToast(
        msg: "Biometric login success (connect this to backend)",
      );

    } catch (e) {
      Fluttertoast.showToast(msg: "Biometric error: $e");
    }
  }


  void _onGoogleLogin() {
    Fluttertoast.showToast(msg: "Google login coming soon");
  }

  void _onAppleLogin() {
    Fluttertoast.showToast(msg: "Apple login coming soon");
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      body: Stack(
        fit: StackFit.expand,
        children: [
          // Background illustration
          Image.asset(
            "assets/login_bg.png",
            fit: BoxFit.cover,
          ),
          Container(
            color: Colors.black.withOpacity(0.4),
          ),
          Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: FadeTransition(
                opacity: _fadeAnim,
                child: SlideTransition(
                  position: _slideAnim,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Logo / Title
                      Hero(
                        tag: "app_logo",
                        child: Icon(
                          Icons.shield_outlined,
                          size: 80,
                          color: theme.colorScheme.primary,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        "OpenResQ",
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: theme.colorScheme.onPrimary,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        "Responder Login",
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.white.withOpacity(0.8),
                        ),
                      ),

                      const SizedBox(height: 40),

                      // Card container
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.surface.withOpacity(0.95),
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              blurRadius: 16,
                              color: Colors.black.withOpacity(0.3),
                            )
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // Email
                            TextField(
                              controller: emailController,
                              keyboardType: TextInputType.emailAddress,
                              decoration: InputDecoration(
                                labelText: "Email",
                                prefixIcon:
                                    const Icon(Icons.email_outlined),
                                errorText: emailError,
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                            ),
                            const SizedBox(height: 16),

                            // Password
                            TextField(
                              controller: passController,
                              obscureText: obscure,
                              decoration: InputDecoration(
                                labelText: "Password",
                                prefixIcon:
                                    const Icon(Icons.lock_outline),
                                suffixIcon: IconButton(
                                  icon: Icon(obscure
                                      ? Icons.visibility
                                      : Icons.visibility_off),
                                  onPressed: () {
                                    setState(() => obscure = !obscure);
                                  },
                                ),
                                errorText: passError,
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                            ),

                            const SizedBox(height: 8),

                            // Remember me + Forgot password
                            Row(
                              children: [
                                Checkbox(
                                  value: rememberMe,
                                  onChanged: (v) {
                                    setState(() => rememberMe = v ?? false);
                                  },
                                ),
                                const Text("Remember me"),
                                const Spacer(),
                                TextButton(
                                  onPressed: () async {
                                    final email = emailController.text.trim();

                                    if (email.isEmpty) {
                                      setState(() {
                                        emailError = "Enter your email first";
                                      });
                                      return;
                                    }

                                    try {
                                      await auth.sendPasswordReset(email);
                                      Fluttertoast.showToast(
                                        msg: "Password reset email sent",
                                      );
                                    } catch (e) {
                                      Fluttertoast.showToast(msg: e.toString());
                                    }
                                  },
                                  child: const Text("Forgot password?"),
                                )

                              ],
                            ),

                            if (generalError != null) ...[
                              const SizedBox(height: 4),
                              Text(
                                generalError!,
                                style: const TextStyle(
                                  color: Colors.red,
                                  fontSize: 12,
                                ),
                              ),
                            ],

                            const SizedBox(height: 12),

                            // Login button
                            SizedBox(
                              height: 48,
                              child: ElevatedButton(
                                onPressed: loading ? null : _onLogin,
                                style: ElevatedButton.styleFrom(
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                ),
                                child: loading
                                    ? const SizedBox(
                                        width: 22,
                                        height: 22,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                          color: Colors.white,
                                        ),
                                      )
                                    : const Text(
                                        "Login",
                                        style: TextStyle(fontSize: 16),
                                      ),
                              ),
                            ),

                            const SizedBox(height: 16),

                            // Social login
                            Row(
                              children: [
                                Expanded(
                                  child: OutlinedButton.icon(
                                    onPressed: _onGoogleLogin,
                                    icon: const Icon(Icons.g_mobiledata),
                                    label: const Text("Google"),
                                    style: OutlinedButton.styleFrom(
                                      shape: RoundedRectangleBorder(
                                        borderRadius:
                                            BorderRadius.circular(12),
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: OutlinedButton.icon(
                                    onPressed: _onAppleLogin,
                                    icon: const Icon(Icons.apple),
                                    label: const Text("Apple"),
                                    style: OutlinedButton.styleFrom(
                                      shape: RoundedRectangleBorder(
                                        borderRadius:
                                            BorderRadius.circular(12),
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),

                            const SizedBox(height: 12),

                            // Biometrics
                            if (canCheckBiometrics)
                              SizedBox(
                                height: 44,
                                child: OutlinedButton.icon(
                                  onPressed: _onBiometricLogin,
                                  icon: const Icon(Icons.fingerprint),
                                  label: const Text("Login with biometrics"),
                                  style: OutlinedButton.styleFrom(
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 20),

                      // Register
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            "Don't have an account?",
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.8),
                            ),
                          ),
                          TextButton(
                            onPressed: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                    builder: (_) => RegisterScreen()),
                              );
                            },
                            child: const Text("Register"),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
