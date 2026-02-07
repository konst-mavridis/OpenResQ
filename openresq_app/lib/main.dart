import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'screens/login_screen.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'services/api_service.dart';

void main() async {
  final api = ApiService();
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  FirebaseMessaging messaging = FirebaseMessaging.instance;
  await messaging.requestPermission(
    alert: true,
    badge: true,
    sound: true,
  );
  String? token = await messaging.getToken();
  if (token != null) {
    debugPrint("Firebase Messaging Token: $token");
    await api.sendPushToken(token);
  }
  FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    debugPrint("FCM Message Received: ${message.messageId}");
    if (message.notification != null) {
      debugPrint('Message notification: ${message.notification}');
    }
  });
  runApp(const OpenResQApp());
}

class OpenResQApp extends StatelessWidget {
  const OpenResQApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OpenResQ',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.red,
      ),
      home: LoginScreen(),
    );
  }
}
