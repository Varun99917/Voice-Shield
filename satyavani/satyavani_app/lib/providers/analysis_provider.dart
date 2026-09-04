import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../models/analysis.dart';
import '../config/app_config.dart';

/// Analysis Provider - Manages voice analysis state
class AnalysisProvider extends ChangeNotifier {
  // Recording state
  bool _isRecording = false;
  bool _isAnalyzing = false;
  String? _recordingPath;

  // Analysis results
  double? _currentRiskScore;
  String? _currentRiskLevel;
  Map<String, dynamic>? _analysisDetails;
  AnalysisResult? _lastResult;

  // History
  List<AnalysisResult> _history = [];
  UserStats? _stats;

  // Error
  String? _error;

  // Getters
  bool get isRecording => _isRecording;
  bool get isAnalyzing => _isAnalyzing;
  double? get currentRiskScore => _currentRiskScore;
  String? get currentRiskLevel => _currentRiskLevel;
  Map<String, dynamic>? get analysisDetails => _analysisDetails;
  AnalysisResult? get lastResult => _lastResult;
  List<AnalysisResult> get history => _history;
  UserStats? get stats => _stats;
  String? get error => _error;

  /// Get risk color based on level
  Color getRiskColor(String? level) {
    switch (level) {
      case 'safe':
      case 'low':
        return Colors.green;
      case 'medium':
        return Colors.yellow.shade700;
      case 'high':
        return Colors.orange;
      case 'critical':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  /// Get risk emoji based on level
  String getRiskEmoji(String? level) {
    switch (level) {
      case 'safe':
      case 'low':
        return '🟢';
      case 'medium':
        return '🟡';
      case 'high':
        return '🟠';
      case 'critical':
        return '🔴';
      default:
        return '⚪';
    }
  }

  /// Get risk label based on level
  String getRiskLabel(String? level) {
    switch (level) {
      case 'safe':
        return 'SAFE';
      case 'low':
        return 'LOW RISK';
      case 'medium':
        return 'MEDIUM RISK';
      case 'high':
        return 'HIGH RISK';
      case 'critical':
        return 'CRITICAL';
      default:
        return 'ANALYZING...';
    }
  }

  /// Load analysis history
  Future<void> loadHistory(String token) async {
    try {
      final response = await http.get(
        Uri.parse('${AppConfig.apiUrl}/analysis/history?limit=20'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _history = (data['analyses'] as List)
            .map((e) => AnalysisResult.fromJson(e))
            .toList();
        notifyListeners();
      }
    } catch (e) {
      _error = 'Failed to load history';
      notifyListeners();
    }
  }

  /// Load user stats
  Future<void> loadStats(String token) async {
    try {
      final response = await http.get(
        Uri.parse('${AppConfig.apiUrl}/analysis/stats'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        _stats = UserStats.fromJson(jsonDecode(response.body));
        notifyListeners();
      }
    } catch (e) {
      _error = 'Failed to load stats';
      notifyListeners();
    }
  }

  /// Simulate voice analysis (for demo without real ML)
  Future<void> analyzeAudio(String token, Uint8List audioBytes) async {
    _isAnalyzing = true;
    _currentRiskScore = null;
    _currentRiskLevel = null;
    _error = null;
    notifyListeners();

    try {
      // Create multipart request
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('${AppConfig.apiUrl}/analysis/analyze'),
      );

      request.headers['Authorization'] = 'Bearer $token';
      request.files.add(
        http.MultipartFile.fromBytes('file', audioBytes, filename: 'audio.m4a'),
      );

      // Send request
      final streamedResponse = await request.send().timeout(
        const Duration(seconds: 30),
      );

      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _lastResult = AnalysisResult.fromJson(data);
        _currentRiskScore = _lastResult!.riskScore;
        _currentRiskLevel = _lastResult!.riskLevel;
        _analysisDetails = _lastResult!.analysisDetails;

        // Refresh history
        await loadHistory(token);
      } else {
        _error = 'Analysis failed';
      }
    } catch (e) {
      // For demo, simulate a result
      _simulateDemoAnalysis();
    }

    _isAnalyzing = false;
    notifyListeners();
  }

  /// Simulate demo analysis result
  void _simulateDemoAnalysis() {
    // Random demo score for visualization
    final random = DateTime.now().millisecondsSinceEpoch % 100;

    if (random < 30) {
      _currentRiskLevel = 'safe';
      _currentRiskScore = 10 + (random % 20).toDouble();
    } else if (random < 60) {
      _currentRiskLevel = 'low';
      _currentRiskScore = 25 + (random % 20).toDouble();
    } else if (random < 80) {
      _currentRiskLevel = 'medium';
      _currentRiskScore = 45 + (random % 15).toDouble();
    } else {
      _currentRiskLevel = 'high';
      _currentRiskScore = 70 + (random % 30).toDouble();
    }
  }

  /// Reset analysis state
  void reset() {
    _isRecording = false;
    _isAnalyzing = false;
    _currentRiskScore = null;
    _currentRiskLevel = null;
    _analysisDetails = null;
    _error = null;
    notifyListeners();
  }

  /// Set recording state
  void setRecording(bool recording, {String? path}) {
    _isRecording = recording;
    _recordingPath = path;
    notifyListeners();
  }

  /// Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
