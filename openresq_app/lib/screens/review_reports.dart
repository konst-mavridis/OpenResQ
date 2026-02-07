import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ReviewReportsPage extends StatefulWidget {
  const ReviewReportsPage({super.key});

  @override
  State<ReviewReportsPage> createState() => _ReviewReportsPageState();
}

class _ReviewReportsPageState extends State<ReviewReportsPage> {
  final ApiService api = ApiService();
  List<Map<String, dynamic>> reports = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _loadReports();
  }

  Future<void> _loadReports() async {
    try {
      final r = await api.getReportsForReview();
      if (!mounted) return;
      setState(() {
        reports = List<Map<String, dynamic>>.from(r);
        loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => loading = false);
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text("Error loading reports: $e")));
    }
  }

  Future<void> _decide(String reportId, String decision) async {
    try {
      await api.decision(reportId, decision);   // <-- ΕΔΩ ΕΙΝΑΙ Η ΔΙΟΡΘΩΣΗ

      setState(() {
        reports.removeWhere((r) => r["id"] == reportId);
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Report $decision successfully")),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Error: $e")),
      );
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Admin Review Panel"),
        backgroundColor: Colors.deepPurple,
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : reports.isEmpty
              ? const Center(
                  child: Text(
                    "No reports for review 🎉",
                    style: TextStyle(fontSize: 18),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: reports.length,
                  itemBuilder: (context, index) {
                    final report = reports[index];

                    double confidence =
                        (report["confidence"] ?? 0.0).toDouble();

                    int upvotes = report["upvotes"] ?? 0;
                    int downvotes = report["downvotes"] ?? 0;

                    return Card(
                      elevation: 4,
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              "Report ID: ${report["id"]}",
                              style: const TextStyle(
                                  fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 6),
                            Text("Description: ${report["description"] ?? "—"}"),

                            const SizedBox(height: 8),

                            Row(
                              children: [
                                Text(
                                  "Confidence: ${confidence.toStringAsFixed(2)}",
                                  style: TextStyle(
                                    color: confidence < 0.2
                                        ? Colors.red
                                        : Colors.green,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                if (confidence < 0.2)
                                  const Padding(
                                    padding: EdgeInsets.only(left: 8),
                                    child: Icon(Icons.warning,
                                        color: Colors.red),
                                  ),
                              ],
                            ),

                            const SizedBox(height: 8),

                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Row(
                                  children: [
                                    const Icon(Icons.thumb_up,
                                        color: Colors.green),
                                    Text(" $upvotes"),
                                    const SizedBox(width: 10),
                                    const Icon(Icons.thumb_down,
                                        color: Colors.red),
                                    Text(" $downvotes"),
                                  ],
                                ),
                                Row(
                                  children: [
                                    ElevatedButton(
                                      style: ElevatedButton.styleFrom(
                                          backgroundColor: Colors.green),
                                      onPressed: () =>
                                          _decide(report["id"], "approved"),
                                      child: const Text("Approve"),
                                    ),
                                    const SizedBox(width: 8),
                                    ElevatedButton(
                                      style: ElevatedButton.styleFrom(
                                          backgroundColor: Colors.red),
                                      onPressed: () =>
                                          _decide(report["id"], "rejected"),
                                      child: const Text("Reject"),
                                    ),
                                  ],
                                )
                              ],
                            )
                          ],
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
