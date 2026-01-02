import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;

  String? get uid => _auth.currentUser?.uid;
  String? get email => _auth.currentUser?.email;

  bool get isLoggedIn => _auth.currentUser != null;

  Future<User?> loginWithEmail(String email, String password) async {
    final cred = await _auth.signInWithEmailAndPassword(email: email, password: password);
    return cred.user;
  }

  // backward-compatible wrapper expected by some screens
  Future<User?> login(String email, String password) async => loginWithEmail(email, password);

  Future<void> logout() async {
    await _auth.signOut();
  }

  Future<String> getIdToken() async {
    final u = _auth.currentUser;
    if (u == null) throw Exception("Not authenticated");
    final token = await u.getIdToken();
    if (token == null) throw Exception('Failed to get id token');
    return token;
  }

  // create account wrapper expected by register screen
  Future<User?> register(String email, String password) async {
    final cred = await _auth.createUserWithEmailAndPassword(email: email, password: password);
    return cred.user;
  }

  // get role & area from backend: implement ApiService.getMe or similar
  // Additionally set up Firebase Messaging token subscription
  Future<void> initFirebaseMessaging() async {
    final fcm = FirebaseMessaging.instance;
    await fcm.requestPermission();
    final token = await fcm.getToken();
    print("FCM token: $token");
    // Optionally send token to your backend to associate with user doc
  }
}
