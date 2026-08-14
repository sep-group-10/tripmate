import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import '../utils/constants.dart';

class ApiException implements Exception {
  final String message;

  ApiException(this.message);

  @override
  String toString() => message;
}

class ApiClient {
  final http.Client _client;
  final FlutterSecureStorage _secureStorage;

  ApiClient({http.Client? client, FlutterSecureStorage? secureStorage})
    : _client = client ?? http.Client(),
      _secureStorage = secureStorage ?? const FlutterSecureStorage();

  Future<Map<String, String>> _buildHeaders() async {
    final headers = <String, String>{'Accept': 'application/json'};
    final token = await _secureStorage.read(key: 'authToken');
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  Future<dynamic> get(String path) async {
    final uri = Uri.parse('$baseUrl$path');
    final headers = await _buildHeaders();

    http.Response response;
    try {
      response = await _client
          .get(uri, headers: headers)
          .timeout(Duration(seconds: requestTimeoutSeconds));
    } on SocketException {
      throw ApiException(
        'Could not reach the backend. Please make sure the server is running.',
      );
    } on TimeoutException {
      throw ApiException('The request timed out. Please try again.');
    } catch (e) {
      throw ApiException('Something went wrong while contacting the server.');
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(
        'Request failed with status ${response.statusCode}.',
      );
    }

    if (response.body.isEmpty) {
      return null;
    }
    return jsonDecode(response.body);
  }
}
