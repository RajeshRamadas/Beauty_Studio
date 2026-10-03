import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../../core/network/api_client.dart';
import '../../../core/theme/app_theme.dart';
import '../../result/screens/result_screen.dart';

class CreateLookScreen extends StatefulWidget {
  final ApiClient apiClient;

  const CreateLookScreen({Key? key, required this.apiClient}) : super(key: key);

  @override
  State<CreateLookScreen> createState() => _CreateLookScreenState();
}

class _CreateLookScreenState extends State<CreateLookScreen> {
  File? _targetFile;
  File? _referenceFile;
  String _category = "Hairstyle";
  final _styleController = TextEditingController();
  final _notesController = TextEditingController();

  bool _isSubmitting = false;
  String? _statusText;

  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage(bool isTarget) async {
    final XFile? picked = await _picker.pickImage(source: ImageSource.gallery);
    if (picked != null) {
      setState(() {
        if (isTarget) {
          _targetFile = File(picked.path);
        } else {
          _referenceFile = File(picked.path);
        }
      });
    }
  }

  Future<void> _submit() async {
    if (_targetFile == null || _referenceFile == null) {
      setState(() {
        _statusText = "Please select both target photo and style reference.";
      });
      return;
    }

    setState(() {
      _isSubmitting = true;
      _statusText = "Submitting request to server...";
    });

    try {
      final res = await widget.apiClient.submitGeneration(
        targetImage: _targetFile!,
        referenceImage: _referenceFile!,
        category: _category,
        style: _styleController.text.trim(),
        notes: _notesController.text.trim(),
      );

      final requestId = res["request_id"];
      setState(() {
        _statusText = "Queued ($requestId). Processing AI transformation...";
      });

      // Poll until finished
      int attempts = 0;
      bool completed = false;
      while (attempts < 60 && !completed) {
        await Future.delayed(const Duration(seconds: 2));
        attempts++;
        final statusRes = await widget.apiClient.pollStatus(requestId);
        final status = statusRes["status"];

        if (status == "succeeded") {
          completed = true;
          if (!mounted) return;
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ResultScreen(
                resultB64: statusRes["result_image_b64"],
                category: _category,
                costFormatted: statusRes["cost_formatted"],
                model: statusRes["model"],
              ),
            ),
          );
        } else if (status == "failed") {
          completed = true;
          throw Exception(statusRes["error_message"] ?? "Generation failed");
        } else {
          setState(() {
            _statusText = "Status: $status... (${attempts * 2}s)";
          });
        }
      }
    } catch (e) {
      setState(() {
        _statusText = "Error: ${e.toString()}";
      });
    } finally {
      setState(() {
        _isSubmitting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Beautiva")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Try the look you love.",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            const Text(
              "Upload your photo plus a style reference. AI transfers the look.",
              style: TextStyle(color: AppTheme.mutedGrey),
            ),
            const SizedBox(height: 16),
            // Target Photo Picker
            _buildImagePickerCard(
              title: "1. Your Photo (Target)",
              file: _targetFile,
              onTap: () => _pickImage(true),
            ),
            const SizedBox(height: 12),
            // Reference Photo Picker
            _buildImagePickerCard(
              title: "2. Style Reference Image",
              file: _referenceFile,
              onTap: () => _pickImage(false),
            ),
            const SizedBox(height: 16),
            // Category Dropdown
            DropdownButtonFormField<String>(
              value: _category,
              decoration: const InputDecoration(
                labelText: "What to transfer",
              ),
              items: ["Hairstyle", "Makeup", "Nail art", "Overall beauty look"]
                  .map((cat) => DropdownMenuItem(value: cat, child: Text(cat)))
                  .toList(),
              onChanged: (val) {
                if (val != null) setState(() => _category = val);
              },
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _styleController,
              decoration: const InputDecoration(
                labelText: "Optional style description",
                hintText: "e.g. soft layered bob",
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _notesController,
              decoration: const InputDecoration(
                labelText: "Optional instructions",
                hintText: "e.g. keep natural hair color",
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _isSubmitting ? null : _submit,
              child: Text(_isSubmitting ? "Applying Style..." : "Apply Style To My Photo"),
            ),
            if (_statusText != null) ...[
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _statusText!.startsWith("Error") ? AppTheme.error.withValues(alpha: 0.12) : AppTheme.surface,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  _statusText!,
                  style: TextStyle(
                    color: _statusText!.startsWith("Error") ? AppTheme.error : AppTheme.textPrimary,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildImagePickerCard({
    required String title,
    required File? file,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppTheme.radius),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: AppTheme.surfaceHigh,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: file != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(10),
                        child: Image.file(file, fit: BoxFit.cover),
                      )
                    : const Icon(Icons.add_a_photo, color: AppTheme.gold),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text(
                      file != null ? "Image selected" : "Tap to select photo",
                      style: const TextStyle(color: AppTheme.mutedGrey, fontSize: 13),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
