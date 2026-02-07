import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

final flutterTts = FlutterTts();

Future<void> speak(String text) async {
  try {
    final response = await http.post(
      Uri.parse('https://api.elevenlabs.io/v1/text-to-speech/iiidtqDt9FBdT1vfBluA'),
      headers: {
        "xi-api-key": "sk_ae012594fd70ce99d87f5561e568aff7d653158a27fb71fb",
        'Content-Type': 'application/json'
      },
      body: jsonEncode({
        'text': text,
        "model_id": "eleven_multilingual_v2",
      }),
    ).timeout(
      const Duration(seconds: 10),
      onTimeout: () => throw Exception('TTS API timeout'),
    );

    if (response.statusCode == 200 && response.bodyBytes.isNotEmpty) {
      try {
        final player = AudioPlayer();
        await player.play(BytesSource(response.bodyBytes));
      } catch (e) {
        // Fallback to flutter_tts if audio player fails
        await flutterTts.speak(text);
      }
    } else {
      // Fallback to flutter_tts if API fails
      await flutterTts.speak(text);
    }
  } catch (e) {
    // Silently fallback to flutter_tts
    try {
      await flutterTts.speak(text);
    } catch (e) {
      // Fail silently if all TTS methods fail
      debugPrint('TTS failed: $e');
    }
  }
}
