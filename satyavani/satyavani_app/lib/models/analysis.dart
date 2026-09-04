/// Analysis Result Model
class AnalysisResult {
  final int id;
  final int userId;
  final double riskScore;
  final String riskLevel;
  final double? spectralScore;
  final double? prosodyScore;
  final double? phaseScore;
  final double? patternScore;
  final Map<String, dynamic>? analysisDetails;
  final double? audioDuration;
  final String? locationCity;
  final String? callerNumber;
  final double? processingTimeMs;
  final String? isAlertSent;
  final DateTime? createdAt;

  AnalysisResult({
    required this.id,
    required this.userId,
    required this.riskScore,
    required this.riskLevel,
    this.spectralScore,
    this.prosodyScore,
    this.phaseScore,
    this.patternScore,
    this.analysisDetails,
    this.audioDuration,
    this.locationCity,
    this.callerNumber,
    this.processingTimeMs,
    this.isAlertSent,
    this.createdAt,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      id: json['id'] ?? 0,
      userId: json['user_id'] ?? 0,
      riskScore: (json['risk_score'] ?? 0).toDouble(),
      riskLevel: json['risk_level'] ?? 'safe',
      spectralScore: json['spectral_score']?.toDouble(),
      prosodyScore: json['prosody_score']?.toDouble(),
      phaseScore: json['phase_score']?.toDouble(),
      patternScore: json['pattern_score']?.toDouble(),
      analysisDetails: json['analysis_details'],
      audioDuration: json['audio_duration']?.toDouble(),
      locationCity: json['location_city'],
      callerNumber: json['caller_number'],
      processingTimeMs: json['processing_time_ms']?.toDouble(),
      isAlertSent: json['is_alert_sent'],
      createdAt: json['created_at'] != null 
          ? DateTime.tryParse(json['created_at']) 
          : null,
    );
  }

  bool get isThreat => riskLevel == 'high' || riskLevel == 'critical';
  
  String get riskEmoji {
    switch (riskLevel) {
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

  String get riskColorHex {
    switch (riskLevel) {
      case 'safe':
      case 'low':
        return '#22c55e';
      case 'medium':
        return '#eab308';
      case 'high':
        return '#f97316';
      case 'critical':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  }
}

/// Analysis History Response
class AnalysisHistory {
  final int total;
  final List<AnalysisResult> analyses;

  AnalysisHistory({
    required this.total,
    required this.analyses,
  });

  factory AnalysisHistory.fromJson(Map<String, dynamic> json) {
    return AnalysisHistory(
      total: json['total'] ?? 0,
      analyses: (json['analyses'] as List? ?? [])
          .map((e) => AnalysisResult.fromJson(e))
          .toList(),
    );
  }
}

/// User Statistics
class UserStats {
  final int totalAnalyses;
  final int todayAnalyses;
  final int threatsDetected;
  final double averageRiskScore;

  UserStats({
    required this.totalAnalyses,
    required this.todayAnalyses,
    required this.threatsDetected,
    required this.averageRiskScore,
  });

  factory UserStats.fromJson(Map<String, dynamic> json) {
    return UserStats(
      totalAnalyses: json['total_analyses'] ?? 0,
      todayAnalyses: json['today_analyses'] ?? 0,
      threatsDetected: json['threats_detected'] ?? 0,
      averageRiskScore: (json['average_risk_score'] ?? 0).toDouble(),
    );
  }
}

/// Live Analysis State
class LiveAnalysisState {
  final bool isRecording;
  final bool isAnalyzing;
  final double? currentScore;
  final String? riskLevel;
  final String? statusMessage;
  final AnalysisResult? result;

  LiveAnalysisState({
    this.isRecording = false,
    this.isAnalyzing = false,
    this.currentScore,
    this.riskLevel,
    this.statusMessage,
    this.result,
  });

  LiveAnalysisState copyWith({
    bool? isRecording,
    bool? isAnalyzing,
    double? currentScore,
    String? riskLevel,
    String? statusMessage,
    AnalysisResult? result,
  }) {
    return LiveAnalysisState(
      isRecording: isRecording ?? this.isRecording,
      isAnalyzing: isAnalyzing ?? this.isAnalyzing,
      currentScore: currentScore ?? this.currentScore,
      riskLevel: riskLevel ?? this.riskLevel,
      statusMessage: statusMessage ?? this.statusMessage,
      result: result ?? this.result,
    );
  }
}
