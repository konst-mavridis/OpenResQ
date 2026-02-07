import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

class LiveRespondersService {
  WebSocketChannel? _channel;

  Stream<Map<String, dynamic>> connect() {
    _channel = WebSocketChannel.connect(
      Uri.parse("wss://10.0.2.2:8000/ws"),
    );

    return _channel!.stream.map((event) {
      return jsonDecode(event);
    });
  }

  void dispose() {
    _channel?.sink.close();
  }
}
