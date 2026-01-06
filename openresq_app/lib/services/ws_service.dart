import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

class WSService {
  WebSocketChannel? _channel;

  void connect() {
    try {
      _channel = WebSocketChannel.connect(Uri.parse("ws://openresq.onrender.com/ws/updates"));
      _channel!.stream.listen((message) {
        try {
          final data = jsonDecode(message);
          // handle updates: e.g. notify listeners / stream controllers in app
          print("WS message: $data");
        } catch (e) {}
      }, onError: (err) {
        print("WS error $err");
        reconnect();
      }, onDone: () {
        reconnect();
      });
    } catch (e) {
      reconnect();
    }
  }

  void reconnect() async {
    await Future.delayed(const Duration(seconds: 5));
    connect();
  }

  void dispose() {
    _channel?.sink.close();
  }
}
