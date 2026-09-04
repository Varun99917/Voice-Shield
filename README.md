# 🎯 Voice Shield - AI-Powered Voice Clone Detection

![Voice Shield](https://img.shields.io/badge/Version-1.0.0-e94560?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python)
![React Native](https://img.shields.io/badge/React%20Native-Expo-000020?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-009688?style=for-the-badge&logo=fastapi)

## 🔒 Overview

**Voice Shield** is an AI-powered real-time detection and prevention system for voice cloning impersonation attacks. Built for SIH 2024 (Smart India Hackathon), this project demonstrates how to identify synthetic/AI-generated voices from authentic human speech.

## 🎯 Problem Statement

Voice cloning technology has advanced rapidly, making it possible to create highly realistic synthetic voices that can be used for fraud, misinformation, and impersonation attacks. This project addresses the challenge of detecting such voice clones in real-time.

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   React Native  │────▶│    FastAPI       │────▶│  DeepVoiceGuard │
│   / Expo App   │     │    Backend       │     │   ML Model API  │
│  (Mobile App)  │     │  (Port 8000)     │     │  (ONNX Runtime) │
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

### Backend (FastAPI + Python)
- 🔒 JWT Authentication
- 📁 Audio file processing
- 🤖 ML model integration (DeepVoiceGuard)
- 💾 SQLite database for analysis history
- ⚡ Async API endpoints
- 📈 Statistics and analytics

### ML Pipeline
- **Spectral Analysis** - Frequency patterns & harmonics
- **Prosody Check** - Pitch, tone & rhythm variations  
- **Phase Analysis** - Signal consistency detection
- **Pattern Recognition** - Synthetic pattern identification

## 🚀 Quick Start

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

# Run on web
npx expo export --platform web
# Then serve with Python
cd dist && python3 -m http.server 8080

# Or run on Expo Go (development)
npx expo start
```

### Default Login
- **Email:** admin@voiceshield.com
- **Password:** admin123

## 📁 Project Structure

```
SIH/
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
```bash
# In voice-shield/backend/.env
DATABASE_URL=sqlite+aiosqlite:///./voiceshield.db
JWT_SECRET=your-secret-key
ML_API_URL=https://deepvoiceguard-api.onrender.com/predict
```

### Frontend API URL
Update in `voice-shield/frontend/src/config.ts`:
```typescript
export const API_BASE_URL = 'http://YOUR_IP:8000';
```

## 🎨 Screenshots

### Home Screen
- Animated pulsing shield
- Real-time statistics
- Quick action cards
- Detection rate visualization

### Analysis Screen
- Audio upload with document picker
- Step-by-step analysis animation
- Sound wave visualization
- Detailed analysis report

### History Screen
- Analysis history list
- Expandable details
- Score breakdown graphs
- Timestamp and file info

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS enabled for development
- Input validation with Pydantic

## 📊 Tech Stack

| Layer | Technology |
|-------|------------|
| Mobile App | React Native + Expo 57 |
| Navigation | Expo Router |
| Icons | Ionicons |
| Backend | FastAPI 0.141.1 |
| Database | SQLite + SQLAlchemy |
| Auth | python-jose + bcrypt |
| ML API | DeepVoiceGuard (RawNet ONNX) |

## 👥 Team

- **Backend & Mobile App Development**
- **ML Team** - ALML/Audio processing
- **Presentation** - PPT preparation

## 📜 License

This project was developed for **SIH 2024** (Smart India Hackathon).

## 🙏 Acknowledgments

- DeepVoiceGuard for the ML model
- FastAPI for the backend framework
- Expo for the mobile development platform
