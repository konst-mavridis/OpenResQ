import 'package:audioplayers/audioplayers.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

Future<void> speak(String text) async {
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
  );

  final player = AudioPlayer();
  await player.play(BytesSource(response.bodyBytes));
}