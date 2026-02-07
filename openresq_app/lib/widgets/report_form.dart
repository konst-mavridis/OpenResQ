import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../services/api_service.dart';
import '../services/storage_service.dart';

class ReportForm extends StatefulWidget {
  const ReportForm({super.key});
  @override
  State<ReportForm> createState() => _ReportFormState();
}

class _ReportFormState extends State<ReportForm> {
  final ApiService api = ApiService();
  final titleController = TextEditingController();
  final descController = TextEditingController();
  final latController = TextEditingController();
  final lngController = TextEditingController();
  String eventType = 'other';
  String severity = 'low';
  bool submitting = false;
  List<File> selectedImages = [];
  bool loadingLocation = false;
  String statusText = '';


  @override
  void dispose() {
    titleController.dispose();
    descController.dispose();
    latController.dispose();
    lngController.dispose();
    super.dispose();
  }

  Future<void> _getCurrentLocation() async {
    setState(() => loadingLocation = true);
    try {
      final permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        final newPermission = await Geolocator.requestPermission();
        if (newPermission == LocationPermission.denied) {
          Fluttertoast.showToast(msg: 'Location permission denied');
          return;
        }
      }
      if (permission == LocationPermission.deniedForever) {
        Fluttertoast.showToast(msg: 'Location permission is permanently denied');
        return;
      }

      final position = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
      setState(() {
        latController.text = position.latitude.toStringAsFixed(6);
        lngController.text = position.longitude.toStringAsFixed(6);
      });
      Fluttertoast.showToast(msg: 'Location updated');
    } catch (e) {
      Fluttertoast.showToast(msg: 'Failed to get location: $e');
    } finally {
      setState(() => loadingLocation = false);
    }
  }

  Future<void> _pickImages() async {
    try {
      final picker = ImagePicker();
      final pickedFiles = await picker.pickMultiImage();
      if (pickedFiles.isNotEmpty) {
        setState(() {
          selectedImages = pickedFiles.map((xf) => File(xf.path)).toList();
        });
        Fluttertoast.showToast(msg: '${selectedImages.length} image(s) selected');
      }
    } catch (e) {
      Fluttertoast.showToast(msg: 'Failed to pick images: $e');
    }
  }

  Future<void> _submit() async {
    if (titleController.text.isEmpty || descController.text.isEmpty) {
      Fluttertoast.showToast(msg: 'Please enter title and description');
      return;
    }

    setState(() => submitting = true);

    try {
      // 🔹 Stage 1: Upload images
      setState(() => statusText = 'Uploading images...');
      List<Map<String, dynamic>> mediaList = [];
      for (var file in selectedImages) {
        final url = await uploadImageToFirebase(file); // η λειτουργική σου
        mediaList.add({"url": url, "type": "image"});
      }

      // 🔹 Stage 2: AI Analysis
      setState(() => statusText = 'Analyzing by AI...');
      // Προαιρετικά: μπορείς να κάνεις call στο backend που τρέχει AI
      final payload = {
        'title': titleController.text.trim(),
        'description': descController.text.trim(),
        'event_type': eventType,
        'severity': severity,
        'latitude': double.tryParse(latController.text) ?? 0.0,
        'longitude': double.tryParse(lngController.text) ?? 0.0,
        'media': mediaList,
      };

      setState(() => statusText = 'Submitting report...');
      await api.createReport(payload);

      Fluttertoast.showToast(msg: 'Report submitted!');
      if (!mounted) return;
      Navigator.pop(context, true);
    } catch (e) {
      Fluttertoast.showToast(msg: 'Failed to submit report: $e');
    } finally {
      if (mounted) {
        setState(() {
        submitting = false;
        statusText = '';
      });
      }
    }
  }


  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: titleController,
              decoration: const InputDecoration(labelText: 'Title'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: descController,
              decoration: const InputDecoration(labelText: 'Description'),
              maxLines: 3,
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    initialValue: eventType,
                    items: const [
                      DropdownMenuItem(value: 'other', child: Text('Other')),
                      DropdownMenuItem(value: 'fire', child: Text('Fire')),
                      DropdownMenuItem(value: 'accident', child: Text('Accident')),
                      DropdownMenuItem(value: 'flood', child: Text('Flood')),
                    ],
                    onChanged: (v) => setState(() => eventType = v ?? 'other'),
                    decoration: const InputDecoration(labelText: 'Event type'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    initialValue: severity,
                    items: const [
                      DropdownMenuItem(value: 'low', child: Text('Low')),
                      DropdownMenuItem(value: 'medium', child: Text('Medium')),
                      DropdownMenuItem(value: 'high', child: Text('High')),
                    ],
                    onChanged: (v) => setState(() => severity = v ?? 'low'),
                    decoration: const InputDecoration(labelText: 'Severity'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: latController,
                    decoration: const InputDecoration(labelText: 'Latitude'),
                    keyboardType: TextInputType.numberWithOptions(decimal: true, signed: true),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: TextField(
                    controller: lngController,
                    decoration: const InputDecoration(labelText: 'Longitude'),
                    keyboardType: TextInputType.numberWithOptions(decimal: true, signed: true),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _pickImages,
                    icon: const Icon(Icons.image),
                    label: const Text('Pick Images'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: loadingLocation ? null : _getCurrentLocation,
                    icon: loadingLocation ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.location_on),
                    label: loadingLocation ? const Text('Getting...') : const Text('Use Location'),
                  ),
                ),
              ],
            ),
            if (selectedImages.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Selected Images:', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: selectedImages.asMap().entries.map((e) {
                        return Stack(
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(4),
                              child: Image.file(e.value, width: 60, height: 60, fit: BoxFit.cover),
                            ),
                            Positioned(
                              top: -8,
                              right: -8,
                              child: GestureDetector(
                                onTap: () {
                                  setState(() => selectedImages.removeAt(e.key));
                                },
                                child: Container(
                                  decoration: const BoxDecoration(color: Colors.red, shape: BoxShape.circle),
                                  padding: const EdgeInsets.all(2),
                                  child: const Icon(Icons.close, color: Colors.white, size: 14),
                                ),
                              ),
                            ),
                          ],
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: submitting ? null : _submit,
                child: submitting ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Text('Submit'),
              ),
            ),
            if (submitting)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Text(statusText, style: TextStyle(fontWeight: FontWeight.bold)),
              ),
          ],
        ),
      ),
    );
  }
}
