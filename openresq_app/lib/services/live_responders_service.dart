import 'dart:async';
import 'dart:convert';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class LiveRespondersService {
  WebSocketChannel? _channel;

  Future<Stream<Map<String, dynamic>>> connect() async {
      final idToken = await FirebaseAuth.instance.currentUser!.getIdToken();
    _channel = WebSocketChannel.connect(
      Uri.parse("ws://10.0.2.2:8000/ws/updates?token=$idToken"),
    );

    return _channel!.stream.map((event) {
      return jsonDecode(event);
    });
  }

  void dispose() {
    _channel?.sink.close();
  }
}
