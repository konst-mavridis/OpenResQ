import 'package:flutter/material.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class ChatScreen extends StatefulWidget {
  final String reportId;
  final String role;

  const ChatScreen({
    super.key,
    required this.reportId,
    required this.role,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ApiService api = ApiService();
  final AuthService auth = AuthService();
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  List<dynamic> messages = [];
  bool loading = true;
  String? myUserId;

  @override
  void initState() {
    super.initState();
    _init();
    _setupFCM();
    _startPolling();
  }

  Future<void> _init() async {
    final me = await api.getMe();
    myUserId = me['id'];
    await _loadMessages();
  }

  // 🔁 Polling κάθε 3 δευτερόλεπτα
  void _startPolling() {
    Future.doWhile(() async {
      await Future.delayed(const Duration(seconds: 3));
      if (!mounted) return false;
      await _loadMessages();
      return true;
    });
  }

  Future<void> _loadMessages() async {
    try {
      final data = await api.getChatMessages(widget.reportId);
      setState(() {
        messages = data;
        loading = false;
      });

      await Future.delayed(const Duration(milliseconds: 100));
      if (_scrollController.hasClients) {
        _scrollController.jumpTo(_scrollController.position.maxScrollExtent);
      }
    } catch (e) {
      debugPrint("Chat load error: $e");
    }
  }

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    _controller.clear();
    await api.sendChatMessage(widget.reportId, text);
    await _loadMessages();
  }

  // 🔔 Push notifications με Firebase
  void _setupFCM() async {
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      if (message.data['reportId'] == widget.reportId) {
        _loadMessages();
      }
    });

    final token = await FirebaseMessaging.instance.getToken();
    if (token != null) {
      await api.sendPushToken(token);
    }
  }

  Widget _bubble(dynamic msg) {
    final isMe = msg['senderId'] == myUserId;
    return Align(
      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
        padding: const EdgeInsets.all(12),
        constraints: const BoxConstraints(maxWidth: 260),
        decoration: BoxDecoration(
          color: isMe ? Colors.blue : Colors.grey.shade300,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          msg['text'],
          style: TextStyle(color: isMe ? Colors.white : Colors.black),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Live Chat")),
      body: Column(
        children: [
          Expanded(
            child: loading
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    controller: _scrollController,
                    itemCount: messages.length,
                    itemBuilder: (_, i) => _bubble(messages[i]),
                  ),
          ),
          SafeArea(
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      hintText: "Γράψε μήνυμα...",
                      contentPadding: EdgeInsets.all(12),
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
