# 🏎️ F1 Race Predictor & Strategy Simulator

A full-stack web application that predicts race outcomes for the 2026 F1 season and enables interactive what-if scenario analysis using machine learning and real-time data.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Project Overview

This project combines data engineering, machine learning, and full-stack development to create an intelligent F1 race prediction platform. Users can:
- View AI-powered predictions for upcoming Grand Prix races
- Explore historical race data and trends (2019-2024)
- Run interactive "what-if" simulations (weather changes, pit strategies, grid penalties)
- Compare prediction accuracy against actual race outcomes

## 🚀 Features

### Current Features
- ✅ FastAPI backend with RESTful API
- ✅ F1 data extraction using FastF1 library
- ✅ Historical race data analysis (2019-2024)
- ✅ Docker containerization support

### In Development
- 🔄 PostgreSQL database with optimized schema
- 🔄 ETL pipeline for historical data ingestion
- 🔄 Machine learning prediction models
- 🔄 Interactive React frontend
- 🔄 Real-time race strategy simulator

### Planned Features
- 📅 Podium probability predictions
- 📅 Fastest lap forecasting
- 📅 Monte Carlo strategy simulation
- 📅 Weather impact analysis
- 📅 WebSocket real-time updates
- 📅 User prediction leaderboards

## 📊 Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **PostgreSQL** - Primary data store for race data
- **Redis** - Caching layer for API responses
- **FastF1** - F1 telemetry and timing data library
- **SQLAlchemy** - ORM for database operations
- **scikit-learn** - Machine learning models
- **pandas** - Data manipulation and analysis

### Frontend (Coming Soon)
- **React** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Recharts / D3.js** - Data visualization
- **TailwindCSS** - Utility-first styling

### DevOps
- **Docker & Docker Compose** - Containerization
- **GitHub Actions** - CI/CD pipeline (planned)
- **AWS/GCP** - Cloud deployment (planned)

## 🏗️ Project Structure
```
f1-predictor/
├── backend/
│   ├── api/                 # API route handlers
│   ├── models/              # ML models and schemas
│   ├── services/            # Business logic layer
│   ├── data/                # Data storage
│   ├── scripts/             # Utility scripts
│   │   ├── explore_fastf1.py    # Data exploration
│   │   └── etl_historical.py    # ETL pipeline
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend container config
├── frontend/                # React application (TBD)
│   ├── src/
│   └── public/
├── docs/                    # Documentation
├── docker-compose.yml       # Multi-container orchestration
├── .gitignore
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Docker & Docker Compose (optional, recommended)
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/Shivam-Lahoti/F1-Predictor.git
cd F1-Predictor
```

2. **Set up Python virtual environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Run the application**
```bash
# Start FastAPI server
uvicorn main:app --reload

# Or run directly
python main.py
```

5. **Access the API**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Setup (Recommended)
```bash
# Start all services (PostgreSQL, Redis, Backend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Explore F1 Data
```bash
cd backend
python scripts/explore_fastf1.py
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints
```
GET  /              - API information
GET  /health        - Health check
GET  /api/races     - List all races (coming soon)
GET  /api/races/{id} - Get race details (coming soon)
POST /api/predict   - Get race predictions (coming soon)
POST /api/simulate  - Run strategy simulation (coming soon)
```

## 🗓️ Development Roadmap

### Week 1: Data Infrastructure ✅ (Current)
- [x] Project setup and structure
- [x] FastAPI backend skeleton
- [x] F1 data exploration with FastF1
- [ ] Database schema design
- [ ] ETL pipeline for historical data
- [ ] Basic API endpoints

### Week 2: Prediction Engine
- [ ] Feature engineering pipeline
- [ ] Train baseline ML models
- [ ] Prediction API endpoints
- [ ] Monte Carlo simulator
- [ ] Redis caching implementation

### Week 3: Frontend Development
- [ ] React app scaffolding
- [ ] Race dashboard UI
- [ ] Prediction visualization
- [ ] Interactive what-if simulator
- [ ] Real-time updates with WebSockets

### Week 4: Deployment & Polish
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Cloud deployment (AWS/GCP)
- [ ] Monitoring and logging
- [ ] Performance optimization
- [ ] Documentation completion

## 🔬 Technical Highlights

### Data Engineering
- ETL pipeline processing 5+ years of F1 historical data
- Efficient data normalization and feature extraction
- Real-time data ingestion capabilities

### Machine Learning
- **Podium Prediction**: Random Forest Classifier with 75%+ accuracy target
- **Lap Time Forecasting**: Regression models with circuit-specific features
- **Strategy Simulation**: Monte Carlo methods for probabilistic outcomes

### System Design
- Microservices architecture with Docker
- RESTful API design with versioning
- Caching strategy for performance optimization
- Scalable database schema design

## 📈 Model Performance (Goals)

| Model | Metric | Target |
|-------|--------|--------|
| Podium Prediction | Accuracy | 75% |
| Fastest Lap | RMSE | < 0.5s |
| Strategy Simulation | Coverage | 90% confidence |

## 🤝 Contributing

This is a personal portfolio project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Shivam Lahoti**
- Graduate Student @ Northeastern University
- MS in Software Engineering Systems
- Research Assistant in Data Engineering
- [GitHub](https://github.com/Shivam-Lahoti)
- [LinkedIn](https://www.linkedin.com/in/shivam-lahoti) *(Update with your actual LinkedIn)*

## 🙏 Acknowledgments

- [FastF1](https://github.com/theOehrly/Fast-F1) - For excellent F1 data access
- [FastAPI](https://fastapi.tiangolo.com/) - For the amazing Python web framework
- [Formula 1](https://www.formula1.com/) - For the inspiration

## 📊 Project Status

**Current Status**: 🚧 Active Development - Week 1

Last Updated: December 21, 2024

---

⭐ Star this repo if you find it interesting!

🏎️ Built with passion for F1 and software engineering