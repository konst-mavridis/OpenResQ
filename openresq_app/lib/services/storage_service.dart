import 'package:firebase_storage/firebase_storage.dart';
import 'dart:io';
import 'package:uuid/uuid.dart';
import 'package:flutter/foundation.dart';

final FirebaseStorage storage = FirebaseStorage.instance;

Future<String> uploadImageToFirebase(File file) async {
  try {
    // Δημιουργούμε ένα μοναδικό όνομα για κάθε εικόνα
    final String fileId = const Uuid().v4();
    final String path = 'reports/$fileId.jpg';

    final ref = storage.ref().child(path);

    // Upload file
    final uploadTask = ref.putFile(file);

    // Προαιρετικά: μπορείς να παρακολουθείς την πρόοδο
    uploadTask.snapshotEvents.listen((event) {
      final progress = (event.bytesTransferred / event.totalBytes) * 100;
      debugPrint('Upload is ${progress.toStringAsFixed(2)}% done');
    });

    final snapshot = await uploadTask;
    
    // Παίρνουμε το URL της εικόνας
    final downloadUrl = await snapshot.ref.getDownloadURL();
    debugPrint('[DEBUG] Uploaded image URL: $downloadUrl');
    return downloadUrl;
  } catch (e) {
    debugPrint('[ERROR] Failed to upload image: $e');
    rethrow;
  }
}
