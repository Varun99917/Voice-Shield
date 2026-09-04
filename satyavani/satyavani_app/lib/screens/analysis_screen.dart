import 'dart:async';
import 'dart:math';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../providers/analysis_provider.dart';
import '../services/audio_service.dart';

/// Analysis Screen - Main voice analysis screen
class AnalysisScreen extends StatefulWidget {
  const AnalysisScreen({super.key});

  @override
  State<AnalysisScreen> createState() => _AnalysisScreenState();
}

class _AnalysisScreenState extends State<AnalysisScreen>
    with TickerProviderStateMixin {
  final AudioService _audioService = AudioService();

  bool _isRecording = false;
  bool _isAnalyzing = false;
  double? _riskScore;
  String? _riskLevel;
  String? _statusMessage;
  int _recordingDuration = 0;
  Timer? _timer;
  Timer? _animationTimer;
  double _pulseScale = 1.0;

  // Demo animation
  List<double> _waveform = [];

  @override
  void initState() {
    super.initState();
    _initAudio();
  }

  Future<void> _initAudio() async {
    final hasPermission = await _audioService.hasPermission();
    if (!hasPermission) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Microphone permission required'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    _animationTimer?.cancel();
    _audioService.dispose();
    super.dispose();
  }

  Future<void> _startRecording() async {
    final hasPermission = await _audioService.hasPermission();
    if (!hasPermission) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please grant microphone permission'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    final path = await _audioService.startRecording();
    if (path != null) {
      setState(() {
        _isRecording = true;
        _recordingDuration = 0;
        _riskScore = null;
        _riskLevel = null;
        _statusMessage = 'Recording...';
        _waveform = [];
      });

      // Start duration timer
      _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
        setState(() {
          _recordingDuration++;
        });
      });

      // Start animation
      _startWaveformAnimation();
    }
  }

  void _startWaveformAnimation() {
    _animationTimer?.cancel();
    _animationTimer = Timer.periodic(const Duration(milliseconds: 100), (
      timer,
    ) {
      if (_isRecording) {
        setState(() {
          // Generate random waveform for demo
          _waveform.add(Random().nextDouble() * 0.8 + 0.2);
          if (_waveform.length > 20) {
            _waveform.removeAt(0);
          }
          // Pulse animation
          _pulseScale =
              1.0 + sin(DateTime.now().millisecondsSinceEpoch / 200) * 0.1;
        });
      }
    });
  }

  Future<void> _stopRecording() async {
    _timer?.cancel();
    _animationTimer?.cancel();

    final path = await _audioService.stopRecording();
    if (path != null) {
      setState(() {
        _isRecording = false;
        _isAnalyzing = true;
        _statusMessage = 'Analyzing voice...';
      });

      // Get audio bytes
      final audioBytes = await _audioService.getAudioBytes(path);

      // Analyze
      final auth = context.read<AuthProvider>();
      final analysis = context.read<AnalysisProvider>();

      if (auth.token != null) {
        await analysis.analyzeAudio(
          auth.token!,
          audioBytes ?? Uint8List(0),
        );

        setState(() {
          _riskScore = analysis.currentRiskScore;
          _riskLevel = analysis.currentRiskLevel;
          _statusMessage = null;
          _isAnalyzing = false;
        });
      } else {
        setState(() {
          _isAnalyzing = false;
          _statusMessage = 'Please login first';
        });
      }

      // Delete recording file
      await _audioService.deleteRecording(path);
    }
  }

  void _reset() {
    setState(() {
      _riskScore = null;
      _riskLevel = null;
      _statusMessage = null;
      _isRecording = false;
      _isAnalyzing = false;
      _recordingDuration = 0;
      _waveform = [];
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [_getBackgroundColor(), Colors.grey.shade100],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Status Bar
              _buildStatusBar(),

              // Main Content
              Expanded(child: _buildMainContent()),

              // Bottom Section
              _buildBottomSection(),
            ],
          ),
        ),
      ),
    );
  }

  Color _getBackgroundColor() {
    if (_riskLevel == 'critical' || _riskLevel == 'high') {
      return Colors.red.shade50;
    } else if (_riskLevel == 'medium') {
      return Colors.orange.shade50;
    } else if (_riskLevel == 'safe' || _riskLevel == 'low') {
      return Colors.green.shade50;
    }
    return Colors.blue.shade50;
  }

  Widget _buildStatusBar() {
    final analysis = context.watch<AnalysisProvider>();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: _getStatusColor().withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: _getStatusColor(),
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  _statusMessage ?? 'Ready to Analyze',
                  style: TextStyle(
                    color: _getStatusColor(),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          const Spacer(),
          if (_isRecording)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.red.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.fiber_manual_record,
                    color: Colors.red,
                    size: 12,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    _formatDuration(_recordingDuration),
                    style: const TextStyle(
                      color: Colors.red,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Color _getStatusColor() {
    if (_riskLevel == 'critical') return Colors.red;
    if (_riskLevel == 'high') return Colors.orange;
    if (_riskLevel == 'medium') return Colors.yellow.shade700;
    if (_riskLevel == 'safe' || _riskLevel == 'low') return Colors.green;
    return Colors.blue;
  }

  Widget _buildMainContent() {
    if (_isAnalyzing) {
      return _buildAnalyzingView();
    }

    if (_riskScore != null) {
      return _buildResultView();
    }

    return _buildRecordingView();
  }

  Widget _buildRecordingView() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Waveform Visualization
        if (_isRecording)
          Container(
            height: 100,
            margin: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: _waveform.map((value) {
                return Container(
                  margin: const EdgeInsets.symmetric(horizontal: 2),
                  width: 8,
                  height: 80 * value,
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(4),
                  ),
                );
              }).toList(),
            ),
          )
        else
          Icon(Icons.mic, size: 80, color: Colors.grey.shade400),

        const SizedBox(height: 30),

        // Main Button
        GestureDetector(
          onTap: _isRecording ? _stopRecording : _startRecording,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: _isRecording ? 100 : 120,
            height: _isRecording ? 100 : 120,
            transform: Matrix4.identity()..scale(_pulseScale),
            transformAlignment: Alignment.center,
            decoration: BoxDecoration(
              color: _isRecording ? Colors.red : Colors.blue,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: (_isRecording ? Colors.red : Colors.blue).withValues(
                    alpha: 0.3,
                  ),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: Icon(
              _isRecording ? Icons.stop : Icons.mic,
              size: 50,
              color: Colors.white,
            ),
          ),
        ),

        const SizedBox(height: 30),

        // Instruction
        Text(
          _isRecording ? 'Tap to stop recording' : 'Tap to start recording',
          style: TextStyle(fontSize: 16, color: Colors.grey.shade600),
        ),

        const SizedBox(height: 8),

        Text(
          'Record 5-10 seconds of voice',
          style: TextStyle(fontSize: 12, color: Colors.grey.shade400),
        ),
      ],
    );
  }

  Widget _buildAnalyzingView() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const SizedBox(
          width: 80,
          height: 80,
          child: CircularProgressIndicator(
            strokeWidth: 6,
            valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
          ),
        ),
        const SizedBox(height: 24),
        const Text(
          '🔍 Analyzing Voice...',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Text(
          'Checking for voice clone patterns',
          style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
        ),
      ],
    );
  }

  Widget _buildResultView() {
    final analysis = context.read<AnalysisProvider>();
    final color = analysis.getRiskColor(_riskLevel);
    final emoji = analysis.getRiskEmoji(_riskLevel);
    final label = analysis.getRiskLabel(_riskLevel);

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Risk Score Circle
        Container(
          width: 200,
          height: 200,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color.withValues(alpha: 0.1),
            border: Border.all(color: color, width: 8),
            boxShadow: [
              BoxShadow(
                color: color.withValues(alpha: 0.3),
                blurRadius: 30,
                spreadRadius: 10,
              ),
            ],
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(emoji, style: const TextStyle(fontSize: 48)),
              const SizedBox(height: 8),
              Text(
                '${_riskScore?.toStringAsFixed(1) ?? 0}%',
                style: TextStyle(
                  fontSize: 36,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
              Text(
                label,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 30),

        // Risk Details
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 20),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(15),
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withValues(alpha: 0.1),
                blurRadius: 10,
                offset: const Offset(0, 5),
              ),
            ],
          ),
          child: Column(
            children: [
              Text(
                _getResultMessage(),
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 14),
              ),
              if (_riskLevel == 'high' || _riskLevel == 'critical') ...[
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.warning, color: Colors.red),
                      const SizedBox(width: 8),
                      const Expanded(
                        child: Text(
                          'Recommended: End call & verify via callback',
                          style: TextStyle(color: Colors.red, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),

        const SizedBox(height: 20),

        // Try Again Button
        OutlinedButton.icon(
          onPressed: _reset,
          icon: const Icon(Icons.refresh),
          label: const Text('Try Again'),
          style: OutlinedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          ),
        ),
      ],
    );
  }

  String _getResultMessage() {
    if (_riskLevel == 'safe' || _riskLevel == 'low') {
      return '✅ Voice appears genuine. No suspicious patterns detected.';
    } else if (_riskLevel == 'medium') {
      return '⚠️ Some unusual patterns detected. Exercise caution.';
    } else if (_riskLevel == 'high') {
      return '🚨 High probability of AI-generated voice. Verify caller identity.';
    } else {
      return '🔴 Critical: Strong indicators of voice cloning detected!';
    }
  }

  Widget _buildBottomSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // Info Text
          if (!_isRecording && _riskScore == null)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.blue.shade700),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Speak clearly into your microphone for best results',
                      style: TextStyle(
                        color: Colors.blue.shade700,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),

          const SizedBox(height: 16),

          // Privacy Note
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.lock, size: 14, color: Colors.grey.shade500),
              const SizedBox(width: 4),
              Text(
                'Your voice data is processed securely and not stored',
                style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _formatDuration(int seconds) {
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
  }
}
