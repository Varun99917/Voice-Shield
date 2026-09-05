# 🎯 Voice Shield - AI-Powered Voice Clone Detection

![Voice Shield](https://img.shields.io/badge/Version-1.0.0-e94560?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python)
![React Native](https://img.shields.io/badge/React%20Native-Expo-000020?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-009688?style=for-the-badge&logo=fastapi)
![SIH 2024](https://img.shields.io/badge/SIH-2024-orange?style=for-the-badge)

## 🔒 Overview

**Voice Shield** is an AI-powered real-time detection and prevention system for voice cloning impersonation attacks. Built for **SIH 2024** (Smart India Hackathon), this project demonstrates how to identify synthetic/AI-generated voices from authentic human speech using advanced ML techniques.

## 🎯 Problem Statement

Voice cloning technology has advanced rapidly, making it possible to create highly realistic synthetic voices that can be used for fraud, misinformation, and impersonation attacks. Voice Shield addresses this challenge by providing a real-time detection system.

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   React Native  │────▶│    FastAPI       │────▶│  DeepVoiceGuard │
│   / Expo App    │     │    Backend       │     │   ML Model API  │
│  (Mobile App)   │     │  (Port 8000)     │     │  (ONNX Runtime) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                        │
        └────────────────────────┘
              REST API + JWT Auth
```

## ✨ Features

### Mobile App (React Native + Expo)
- 🎤 Audio upload for voice analysis
- 📊 Real-time analysis with animated UI
- 📈 Detailed score breakdown (Spectral, Prosody, Phase, Pattern)
- 📜 Analysis history with expandable details
- 🔐 JWT-based authentication
- 🎨 Dark cyber-security theme UI
- 📱 Works on both Web and Mobile (Expo Go)

### Backend (FastAPI + Python)
- 🔒 JWT Authentication
- 📁 Audio file processing
- 🤖 ML model integration (DeepVoiceGuard)
- 💾 SQLite database for analysis history
- ⚡ Async API endpoints
- 📈 Statistics and analytics
- 🛡️ CORS enabled
- 🔄 Fallback mechanism if ML API fails

### ML Pipeline
- **Spectral Analysis** - Frequency patterns & harmonics
- **Prosody Check** - Pitch, tone & rhythm variations
- **Phase Analysis** - Signal consistency detection
- **Pattern Recognition** - Synthetic pattern identification

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- pnpm or npm

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd voice-shield/backend
pip install -r requirements.txt

# Run backend
python main.py
```

Backend will start at `http://localhost:8000`
API docs available at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd voice-shield/frontend

# Install dependencies
npm install
# or
pnpm install

# Build for web
npx expo export --platform web
cd dist && python3 -m http.server 8080

# Or run on Expo Go (development)
npx expo start
```

### Default Login
- **Email:** admin@voiceshield.com
- **Password:** admin123

## 📁 Project Structure

```
Voice-Shield/
├── voice-shield/
│   ├── backend/
│   │   ├── api/
│   │   │   ├── analysis.py    # Voice analysis endpoints
│   │   │   └── auth.py        # Authentication endpoints
│   │   ├── core/
│   │   │   ├── config.py      # Configuration settings
│   │   │   ├── database.py    # Database connection
│   │   │   └── security.py    # JWT utilities
│   │   ├── models/
│   │   │   └── models.py      # SQLAlchemy models
│   │   ├── services/
│   │   │   └── ml_service.py  # ML API integration
│   │   ├── main.py            # FastAPI app entry
│   │   └── requirements.txt
│   │
│   ├── frontend/
│   │   ├── app/
│   │   │   ├── (tabs)/
│   │   │   │   ├── index.tsx  # Home screen
│   │   │   │   ├── analyze.tsx # Analysis screen
│   │   │   │   ├── history.tsx # History screen
│   │   │   │   └── profile.tsx # Profile screen
│   │   │   └── index.tsx      # Login screen
│   │   ├── src/
│   │   │   ├── authStore.ts   # Auth state management
│   │   │   ├── config.ts      # API configuration
│   │   │   ├── services/
│   │   │   │   └── api.ts     # API service layer
│   │   │   └── types.ts      # TypeScript types
│   │   └── package.json
│   │
│   ├── start.sh               # Auto-start script
│   └── fix-ip.sh             # IP fix script
│
└── README.md
```

## 🔧 Configuration

### Backend Environment
```python
# In voice-shield/backend/core/config.py
DATABASE_URL = "sqlite+aiosqlite:///./voiceshield.db"
JWT_SECRET = "your-secret-key"
ML_API_URL = "https://deepvoiceguard-api.onrender.com/predict"
```

### Frontend API URL
Update in `voice-shield/frontend/src/config.ts`:
```typescript
export const API_BASE_URL = 'http://YOUR_IP:8000';
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login & get JWT token
- `GET /api/auth/me` - Get current user info

### Analysis
- `POST /api/analysis/analyze` - Analyze uploaded audio file
- `POST /api/analysis/analyze-demo` - Demo analysis (with force_result query)
- `POST /api/analysis/analyze-upload` - Upload via JSON base64
- `GET /api/analysis/history` - Get user's analysis history
- `GET /api/analysis/stats` - Get user's statistics

## 📊 Database Schema

### Users Table
- `id`, `email`, `password_hash`, `full_name`, `role`, `created_at`

### Analyses Table
- `id`, `user_id`, `audio_filename`, `risk_score`, `risk_level`
- `is_cloned`, `confidence`, `spectral_score`, `prosody_score`
- `phase_score`, `pattern_score`, `analysis_details`, `ml_source`
- `created_at`

### Alerts Table
- `id`, `user_id`, `analysis_id`, `alert_type`, `severity`
- `title`, `message`, `status`, `is_resolved`, `created_at`

## 🎨 UI Screens

### Home Screen
- Animated pulsing shield
- Real-time statistics
- Quick action cards (clickable with navigation)
- Detection rate visualization
- How It Works section

### Analysis Screen
- Audio upload with document picker
- Step-by-step analysis animation
- Sound wave visualization
- Detailed analysis report
- File info with timestamp
- ML source tracking

### History Screen
- Analysis history list
- Expandable details on tap
- Score breakdown graphs
- Timestamp and file info
- Key observations
- Safety recommendations

## 🔐 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS enabled for development
- Input validation with Pydantic
- User-specific data isolation
- Secure file handling

## 📊 Tech Stack

| Layer | Technology |
|-------|------------|
| Mobile App | React Native + Expo 57 |
| Navigation | Expo Router |
| Icons | Ionicons (@expo/vector-icons) |
| HTTP Client | Fetch API |
| Backend | FastAPI 0.141.1 |
| Database | SQLite + SQLAlchemy 2.0.52 |
| Auth | python-jose + bcrypt |
| ML API | DeepVoiceGuard (RawNet ONNX) |
| Async | asyncio + greenlet |

## 🚀 Future Enhancements

- Real-time phone call detection
- Multi-language support
- Browser extension
- WhatsApp/Telegram bot integration
- More ML models (Wav2Vec, AASIST)
- Speaker verification system
- Cloud deployment (AWS/Azure)
- Docker containerization
- Load balancing & scaling

## 👥 Team

- **Team Lead & Developer** - Mobile App + Backend Development
- **ML Team** (3 members) - Audio processing, model training, ALML
- **Presentation** - PPT preparation
- **Helper** - General support

## 📜 License

This project was developed for **SIH 2024** (Smart India Hackathon).

## 🙏 Acknowledgments

- DeepVoiceGuard for the ML model
- FastAPI for the backend framework
- Expo for the mobile development platform
- Smart India Hackathon 2024 for the opportunity

## 📞 Contact

For queries, reach out to the team through SIH 2024 platform.

---

**Made with ❤️ for SIH 2024**
