import 'dart:async';
import 'dart:html' as html;
import 'dart:typed_data';

/// Audio Service - Handles audio recording using Web APIs
class AudioService {
  bool _isRecording = false;
  List<double> _audioData = [];
  Timer? _recordingTimer;
  DateTime? _startTime;

  /// Check if recording is in progress
  bool get isRecording => _isRecording;

  /// Check microphone permission
  Future<bool> hasPermission() async {
    try {
      // Request microphone access via browser
      final stream = await html.window.navigator.mediaDevices?.getUserMedia({'audio': true});
      if (stream != null) {
        // Stop tracks immediately, we just wanted permission
        stream.getTracks().forEach((track) => track.stop());
        return true;
      }
      return false;
    } catch (e) {
      // ignore: avoid_print
      print('Permission error: $e');
      return false;
    }
  }

  /// Start recording audio (simulated for demo)
  Future<String?> startRecording() async {
    try {
      if (!await hasPermission()) {
        return null;
      }

      _isRecording = true;
      _audioData = [];
      _startTime = DateTime.now();
      _recordingTimer?.cancel();
      return 'web_recording';
    } catch (e) {
      // ignore: avoid_print
      print('Error starting recording: $e');
      return null;
    }
  }

  /// Stop recording and return simulated audio data
  Future<String?> stopRecording() async {
    try {
      if (!_isRecording) return null;
      _isRecording = false;
      _recordingTimer?.cancel();
      return 'web_recording';
    } catch (e) {
      // ignore: avoid_print
      print('Error stopping recording: $e');
      return null;
    }
  }

  /// Get audio bytes (returns simulated data for demo)
  Future<Uint8List?> getAudioBytes(String path) async {
    try {
      // Generate simulated audio bytes for demo
      final random = DateTime.now().millisecondsSinceEpoch;
      final length = 32000; // 2 seconds of simulated 16kHz audio
      final bytes = Uint8List(length);

      for (int i = 0; i < length; i++) {
        bytes[i] = (random * i) % 256;
      }

      return bytes;
    } catch (e) {
      // ignore: avoid_print
      print('Error reading audio file: $e');
      return null;
    }
  }

  /// Delete recording (no-op for demo)
  Future<void> deleteRecording(String path) async {
    // No file to delete in web demo
  }

  /// Dispose
  Future<void> dispose() async {
    _recordingTimer?.cancel();
    _isRecording = false;
  }
}
