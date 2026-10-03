import 'package:flutter/material.dart';
import '../../../core/network/api_client.dart';
import '../../../core/theme/app_theme.dart';
import '../../result/screens/result_screen.dart';

class HistoryScreen extends StatefulWidget {
  final ApiClient apiClient;

  const HistoryScreen({Key? key, required this.apiClient}) : super(key: key);

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<dynamic> _history = [];
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    if (widget.apiClient.authToken == null) return;

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final list = await widget.apiClient.listHistory();
      setState(() {
        _history = list;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _deleteItem(String id) async {
    try {
      await widget.apiClient.deleteGeneration(id);
      setState(() {
        _history.removeWhere((item) => item["request_id"] == id);
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Failed deleting item: ${e.toString()}")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.apiClient.authToken == null) {
      return Scaffold(
        appBar: AppBar(title: const Text("My Saved Looks")),
        body: const Center(
          child: Text(
            "Please sign in on the Account tab to view your generation history.",
            textAlign: TextAlign.center,
            style: TextStyle(color: AppTheme.mutedGrey),
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text("My Saved Looks"),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadHistory,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text("Error: $_error"))
              : _history.isEmpty
                  ? const Center(child: Text("No saved looks found."))
                  : ListView.builder(
                      padding: const EdgeInsets.all(12),
                      itemCount: _history.length,
                      itemBuilder: (context, index) {
                        final item = _history[index];
                        final reqId = item["request_id"];
                        final category = item["category"] ?? "Style";
                        final status = item["status"] ?? "unknown";
                        final date = item["created_at"] ?? "";
                        final imgB64 = item["result_image_b64"];

                        return Card(
                          margin: const EdgeInsets.only(bottom: 12),
                          child: ListTile(
                            title: Text(category, style: const TextStyle(fontWeight: FontWeight.bold)),
                            subtitle: Text("Status: $status • $date", style: const TextStyle(fontSize: 12)),
                            trailing: IconButton(
                              icon: const Icon(Icons.delete_outline, color: AppTheme.error),
                              onPressed: () => _deleteItem(reqId),
                            ),
                            onTap: imgB64 != null
                                ? () {
                                    Navigator.push(
                                      context,
                                      MaterialPageRoute(
                                        builder: (_) => ResultScreen(
                                          resultB64: imgB64,
                                          category: category,
                                          costFormatted: item["cost_formatted"],
                                          model: item["model"],
                                        ),
                                      ),
                                    );
                                  }
                                : null,
                          ),
                        );
                      },
                    ),
    );
  }
}
