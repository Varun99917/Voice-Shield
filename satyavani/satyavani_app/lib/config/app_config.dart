/// App Configuration
/// Centralized configuration for the SatyVaani app
library;

class AppConfig {
  // ⚠️ IMPORTANT: Isko apne Mac ka IP address daalo!
  // Terminal mein ye command chalao: ifconfig | grep "inet "
  // Jo IP dikhe (127.0.0.1 ya localhost nahi) wo daalo
  // Example: 192.168.0.100 ya 192.168.1.50
  static const String macIp = '192.168.0.100'; // <-- YAHAN APNA IP DAALO!
  static const int backendPort = 8000;

  // API Configuration
  static const String baseUrl = 'http://$macIp:$backendPort';
  static const String apiUrl = '$baseUrl/api';
  static const String wsUrl = 'ws://$macIp:$backendPort';

  // Timeouts
  static const int connectionTimeout = 30000;
  static const int receiveTimeout = 30000;

  // Audio Settings
  static const int audioSampleRate = 16000;
  static const int audioChunkDuration = 2;

  // Risk Thresholds
  static const double lowRiskThreshold = 40;
  static const double mediumRiskThreshold = 60;
  static const double highRiskThreshold = 80;

  // App Info
  static const String appName = 'SatyVaani';
  static const String appVersion = '1.0.0';
  static const String appTagline = 'Voice Clone Detection';
}
