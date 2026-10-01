import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiClient {
  final String baseUrl;
  String? authToken;

  ApiClient({this.baseUrl = "http://127.0.0.1:8000/api/v1"});

  Map<String, String> get _headers {
    final headers = {"Accept": "application/json"};
    if (authToken != null) {
      headers["Authorization"] = "Bearer $authToken";
    }
    return headers;
  }

  Future<Map<String, dynamic>> register(String email, String password) async {
    final response = await http.post(
      Uri.parse("$baseUrl/auth/register"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"email": email, "password": password}),
    );
    return _handleResponse(response);
  }

  Future<String> login(String email, String password) async {
    final response = await http.post(
      Uri.parse("$baseUrl/auth/token"),
      headers: {"Content-Type": "application/x-www-form-urlencoded"},
      body: {"username": email, "password": password},
    );
    final data = _handleResponse(response);
    authToken = data["access_token"];
    return authToken!;
  }

  Future<Map<String, dynamic>> submitGeneration({
    required File targetImage,
    required File referenceImage,
    required String category,
    String style = "",
    String notes = "",
  }) async {
    final request = http.MultipartRequest("POST", Uri.parse("$baseUrl/generations"));
    request.headers.addAll(_headers);

    request.fields["category"] = category;
    request.fields["style"] = style;
    request.fields["notes"] = notes;

    request.files.add(await http.MultipartFile.fromPath("target_image", targetImage.path));
    request.files.add(await http.MultipartFile.fromPath("reference_image", referenceImage.path));

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> pollStatus(String requestId) async {
    final response = await http.get(
      Uri.parse("$baseUrl/generations/$requestId"),
      headers: _headers,
    );
    return _handleResponse(response);
  }

  Future<List<dynamic>> listHistory() async {
    final response = await http.get(
      Uri.parse("$baseUrl/generations"),
      headers: _headers,
    );
    final data = _handleResponse(response);
    return data as List<dynamic>;
  }

  Future<void> deleteGeneration(String requestId) async {
    final response = await http.delete(
      Uri.parse("$baseUrl/generations/$requestId"),
      headers: _headers,
    );
    if (response.statusCode != 204 && response.statusCode != 200) {
      throw Exception("Failed deleting request $requestId");
    }
  }

  dynamic _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body);
    }
    final errorJson = jsonDecode(response.body);
    final message = errorJson["detail"] ?? errorJson["message"] ?? "HTTP ${response.statusCode} Error";
    throw Exception(message);
  }
}
