# 🛡️ SatyVaani Backend

AI-Powered Voice Clone Detection System - Backend API

## 🚀 Quick Start

### Option 1: Run Locally (Recommended for Development)

```bash
# 1. Navigate to backend folder
cd satyavani/backend

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate  # On Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start server
python main.py
```

### Option 2: Using Docker

```bash
# Build image
docker build -t satyavani-backend .

# Run container
docker run -p 8000:8000 satyavani-backend
```

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔑 Default Credentials

| Email | Password | Role |
|-------|----------|------|
| admin@satyavani.com | admin123 | Admin |

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/profile` | Get profile |
| PUT | `/api/auth/profile` | Update profile |

### Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analysis/analyze` | Analyze audio file |
| GET | `/api/analysis/history` | Get analysis history |
| GET | `/api/analysis/recent` | Get recent analyses |
| GET | `/api/analysis/stats` | Get user stats |

### Dashboard (Admin)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/overview` | Dashboard overview |
| GET | `/api/dashboard/threat-trends` | Threat trends |
| GET | `/api/dashboard/recent-alerts` | Recent alerts |
| GET | `/api/dashboard/model-performance` | Model metrics |

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts/` | Get my alerts |
| PUT | `/api/alerts/{id}/acknowledge` | Acknowledge alert |
| PUT | `/api/alerts/{id}/resolve` | Resolve alert |

### WebSocket
| Protocol | Endpoint | Description |
|----------|----------|-------------|
| WS | `/ws/analysis/{token}` | Real-time audio analysis |
| WS | `/ws/admin/{token}` | Admin monitoring |

## 🧪 Testing the API

### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Analyze Audio
```bash
curl -X POST http://localhost:8000/api/analysis/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@audio.wav"
```

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── start.sh           # Quick start script
├── core/              # Core modules
│   ├── config.py      # Settings
│   ├── database.py    # Database setup
│   └── security.py    # JWT & auth
├── models/            # Database models
│   ├── user.py        # User model
│   ├── analysis.py    # Analysis model
│   └── alert.py       # Alert model
├── api/               # API endpoints
│   ├── auth.py        # Authentication
│   ├── analysis.py    # Audio analysis
│   ├── dashboard.py   # Admin dashboard
│   ├── alerts.py      # Alert management
│   └── websocket.py   # WebSocket
└── services/          # Business logic
    ├── ml_service.py  # ML model integration
    ├── audio_service.py # Audio processing
    ├── risk_engine.py # Risk scoring
    └── notification.py # Notifications
```

## 🔧 Environment Variables

Create a `.env` file:

```env
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite+aiosqlite:///./satyavani.db
```

## 🤝 Team

**Smart India Hackathon 2024**

- Backend: FastAPI + PostgreSQL
- ML: PyTorch + Librosa
- Frontend: Flutter + React

---

Made with ❤️ for Smart India Hackathon
