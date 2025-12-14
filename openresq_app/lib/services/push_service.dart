import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class PushService {
  final FirebaseMessaging _fcm = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _local = FlutterLocalNotificationsPlugin();

  Future<void> init() async {
    // request permission
    await _fcm.requestPermission();
    // init local notifications for foreground
    const androidInit = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosInit = DarwinInitializationSettings();
    await _local.initialize(const InitializationSettings(android: androidInit, iOS: iosInit));
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      _showLocal(message.notification?.title ?? "OpenResQ", message.notification?.body ?? "");
    });
  }

  Future<void> _showLocal(String title, String body) async {
    const androidDetails = AndroidNotificationDetails('openresq', 'OpenResQ', importance: Importance.max, priority: Priority.high);
    const platform = NotificationDetails(android: androidDetails);
    await _local.show(0, title, body, platform);
  }
}
