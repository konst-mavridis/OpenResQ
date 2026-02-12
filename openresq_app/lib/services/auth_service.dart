import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final FirebaseFirestore _db = FirebaseFirestore.instance;

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
Future<void> register(
  String email,
  String password, {
  required String displayName,
  String? inviteToken,
  required String selectedRole, // "citizen" or "responder"
}) async {
  // Create Firebase user
  final userCred = await _auth.createUserWithEmailAndPassword(
    email: email,
    password: password,
  );

  final uid = userCred.user!.uid;

  await userCred.user!.updateDisplayName(displayName);

  // Default role is always citizen
  String finalRole = "citizen";

  // If user selected responder → create pending request
  if (selectedRole == "responder") {
    await _db.collection("responder_requests").doc(uid).set({
      "userId": uid,
      "email": email,
      "displayName": displayName,
      "status": "pending",
      "timestamp": FieldValue.serverTimestamp(),
    });
  }

  // If invite token exists → override role (admin invited them)
  if (inviteToken != null && inviteToken.isNotEmpty) {
    final inviteDoc = await _db.collection("invites").doc(inviteToken).get();

    if (inviteDoc.exists) {
      final data = inviteDoc.data()!;
      if (data["email"] == email) {
        finalRole = data["role"]; // usually "responder"
      }
    }
  }

  // Save user profile
  await _db.collection("users").doc(uid).set({
    "uid": uid,
    "email": email,
    "displayName": displayName,
    "role": finalRole, // citizen OR responder (if invited)
    "createdAt": DateTime.now().toIso8601String(),
  });
}
// get role & area from backend: implement ApiService.getMe or similar
  // Additionally set up Firebase Messaging token subscription
  Future<void> initFirebaseMessaging() async {
    final fcm = FirebaseMessaging.instance;
    await fcm.requestPermission();
    final token = await fcm.getToken();
    debugPrint("FCM token: $token");
    // Optionally send token to your backend to associate with user doc
  }

  Future<void> sendPasswordReset(String email) async { 
    await _auth.sendPasswordResetEmail(email: email); 
  }
}
