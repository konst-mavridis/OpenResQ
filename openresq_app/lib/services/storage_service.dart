import 'dart:io';
import 'package:firebase_storage/firebase_storage.dart';

class StorageService {
  final FirebaseStorage storage = FirebaseStorage.instance;

  Future<String> uploadFile(File file) async {
    final path = "reports/${DateTime.now().millisecondsSinceEpoch}.jpg";
    final ref = storage.ref().child(path);

    final UploadTask task = ref.putFile(file);
    final TaskSnapshot snap = await task;
    final String url = await snap.ref.getDownloadURL();
    return url;
  }
}
