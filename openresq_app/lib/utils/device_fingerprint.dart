import 'dart:convert';
import 'dart:io';
import 'package:crypto/crypto.dart';
import 'package:device_info_plus/device_info_plus.dart';

class DeviceFingerprint {
  static Future<String> generate() async {
    final deviceInfo = DeviceInfoPlugin();

    String raw;

    if (Platform.isAndroid) {
      final info = await deviceInfo.androidInfo;
      raw = "${info.id}-${info.model}-${info.version.sdkInt}";
    } else if (Platform.isIOS) {
      final info = await deviceInfo.iosInfo;
      raw = "${info.identifierForVendor}-${info.systemVersion}";
    } else {
      raw = "unknown-device";
    }

    return sha256.convert(utf8.encode(raw)).toString();
  }
}
