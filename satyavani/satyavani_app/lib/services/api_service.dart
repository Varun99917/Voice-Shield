import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import '../models/user.dart';
import '../models/analysis.dart';

/// API Service - Handles all HTTP requests to backend
class ApiService {
  String? _token;

  /// Set authentication token
  void setToken(String token) {
    _token = token;
  }

  /// Clear token on logout
  void clearToken() {
    _token = null;
  }

  /// Get headers with authentication
  Map<String, String> get _headers {
    final headers = {'Content-Type': 'application/json'};
    if (_token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    return headers;
  }

  // ==================== AUTH ====================

  /// Login user
  Future<LoginResponse> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('${AppConfig.apiUrl}/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return LoginResponse.fromJson(data);
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Login failed');
    }
  }

  /// Register user
  Future<LoginResponse> register({
    required String email,
    required String password,
    required String fullName,
    String? phoneNumber,
    String? organization,
  }) async {
    final response = await http.post(
      Uri.parse('${AppConfig.apiUrl}/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
        'full_name': fullName,
        'phone_number': ?phoneNumber,
        'organization': ?organization,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return LoginResponse.fromJson(data);
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Registration failed');
    }
  }

  /// Get current user profile
  Future<User> getProfile() async {
    final response = await http.get(
      Uri.parse('${AppConfig.apiUrl}/auth/profile'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return User.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load profile');
    }
  }

  // ==================== ANALYSIS ====================

  /// Get analysis history
  Future<AnalysisHistory> getAnalysisHistory({
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await http.get(
      Uri.parse(
        '${AppConfig.apiUrl}/analysis/history?limit=$limit&offset=$offset',
      ),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return AnalysisHistory.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load analysis history');
    }
  }

  /// Get recent analyses
  Future<List<AnalysisResult>> getRecentAnalyses({int limit = 5}) async {
    final response = await http.get(
      Uri.parse('${AppConfig.apiUrl}/analysis/recent?limit=$limit'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => AnalysisResult.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load recent analyses');
    }
  }

  /// Get user statistics
  Future<UserStats> getUserStats() async {
    final response = await http.get(
      Uri.parse('${AppConfig.apiUrl}/analysis/stats'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return UserStats.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load stats');
    }
  }

  // ==================== ALERTS ====================

  /// Get alerts
  Future<List<dynamic>> getAlerts({int limit = 20}) async {
    final response = await http.get(
      Uri.parse('${AppConfig.apiUrl}/alerts/?limit=$limit'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load alerts');
    }
  }

  /// Get unread alert count
  Future<int> getUnreadAlertCount() async {
    final response = await http.get(
      Uri.parse('${AppConfig.apiUrl}/alerts/unread-count'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body)['unread_count'] ?? 0;
    } else {
      return 0;
    }
  }
}
