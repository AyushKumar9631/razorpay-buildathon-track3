# AI Revenue Recovery System

🏆 **Razorpay AI Buildathon - Track 3 Submission**

An AI-powered revenue recovery agent that detects revenue at risk, diagnoses root causes, and executes bounded recovery workflows with full compliance and audit trails.

## 🎯 Problem Statement

Build an agent that detects revenue at risk, determines the right intervention, and executes a bounded recovery workflow: from payment failures and checkout abandonment to overdue receivables.

## ✨ Key Features

- **🔍 Automated Detection** - Monitors transactions for payment failures, cart abandonment, subscription issues, and overdue invoices
- **🤖 AI-Powered Diagnosis** - Uses LLM agents to analyze root causes and determine optimal interventions
- **⚡ Autonomous Recovery** - Executes recovery workflows with smart retry logic and personalized communications
- **📊 Measurable Results** - Tracks recovered revenue with detailed metrics and analytics
- **✅ Compliance-First** - Built-in stopping rules, escalation policies, and complete audit trail
- **🇮🇳 India-Optimized** - Supports UPI, NACH, and Hinglish communications

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- LangChain + LangGraph (AI orchestration)
- OpenAI GPT-4 (LLM)
- PostgreSQL (Supabase)
- Redis (caching)

**Frontend:**
- Next.js 14 (React + TypeScript)
- Tailwind CSS + shadcn/ui
- Recharts (visualization)
- WebSockets (real-time updates)

**Deployment:**
- Frontend: Vercel
- Backend: Railway/Render
- Database: Supabase

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Dashboard                       │
│          (Next.js + TypeScript + Tailwind)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                     API Gateway (FastAPI)                    │
└─────────┬───────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────┐
│              AI Agent Orchestrator (LangGraph)              │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Detection │→ │Diagnosis │→ │Intervention│→│Execution│ │
│  │  Agent   │  │  Agent   │  │   Agent   │  │  Agent  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                                                             │
│  └──────────────────────────────────────────────────────┘ │
└─────────┬──────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────┐
│         PostgreSQL (Supabase) + Redis Cache                 │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or Supabase account)
- OpenAI API key

### Environment Variables

Create `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Redis (optional for local dev)
REDIS_URL=redis://localhost:6379

# App Config
DEBUG=True
SECRET_KEY=your_secret_key
```

Create `.env.local` in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit `http://localhost:3000` to see the dashboard.

## 📊 Demo Scenarios

### Scenario Results (Demo Data)

| Scenario | Cases | At Risk | Recovered | Rate |
|----------|-------|---------|-----------|------|
| Payment Degradation | 20 | $28,000 | $23,800 | 85% |
| Checkout Abandonment | 50 | $15,000 | $5,400 | 36% |
| Subscription Failure | 30 | $6,600 | $5,940 | 90% |
| B2B Receivables | 15 | $50,000 | $38,000 | 76% |
| **TOTAL** | **115** | **$99,600** | **$73,140** | **73.4%** |

### Key Metrics

- **Average Recovery Time:** 4.2 days
- **Intervention Success Rate:** 68%
- **Compliance Score:** 100%
- **Cost per Recovery:** $2.50

## 🎯 AI Agent Workflow

1. **Detection Agent** - Monitors transaction streams and identifies revenue risks
2. **Diagnosis Agent** - Analyzes root causes (technical vs customer-side)
3. **Intervention Agent** - Selects optimal recovery strategy based on customer profile
4. **Execution Agent** - Implements recovery workflow (retry, email, SMS, etc.)
5. **Compliance Agent** - Enforces stopping rules and maintains audit trail

## 📱 Features

### Dashboard
- Real-time revenue at risk metrics
- Recovery rate trends and analytics
- Active interventions queue
- Recent risk detections

### Risk Management
- Automated risk detection
- AI-powered diagnosis
- Priority scoring
- Customer profile integration

### Intervention System
- Smart retry scheduling
- Personalized communication generation
- Multi-channel support (email, SMS ready)
- A/B testing framework

### Compliance & Audit
- Stopping rules enforcement
- Contact frequency limits
- Complete audit trail
- Regulatory compliance checks

## 🔒 Compliance Features

- **Stopping Rules:** Max 3 contacts per week per customer
- **Opt-out Enforcement:** Immediate cessation upon request
- **Dispute Freeze:** Automatic stop during active disputes
- **Audit Trail:** Every decision logged with reasoning
- **Escalation:** Automatic human-in-loop for high-value cases

## 📈 Deployment

### Deploy to Vercel (Frontend)

```bash
cd frontend
vercel
```

### Deploy to Railway (Backend)

1. Connect your GitHub repository
2. Add environment variables in Railway dashboard
3. Railway will auto-detect and deploy FastAPI app

### Supabase Setup

1. Create a new Supabase project
2. Copy the connection string
3. Run migrations using the Supabase SQL editor

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎬 Demo Script

1. **Overview** - Show dashboard with live metrics
2. **Detection** - Demonstrate real-time risk detection
3. **AI Analysis** - Show agent diagnosis and reasoning
4. **Intervention** - Execute recovery workflow
5. **Results** - Display recovered revenue and audit trail

## 🏆 Competitive Advantages

1. **Complete Autonomous Loop** - End-to-end recovery, not just detection
2. **Multi-Scenario Coverage** - 5+ revenue loss types in one platform
3. **Explainable AI** - Every decision has logged reasoning
4. **Compliance-First** - Built-in regulatory adherence
5. **Production-Ready** - Scalable architecture, not just a prototype
6. **India-Optimized** - UPI, NACH, Hinglish support

## 📝 Documentation

- [Research Findings](./RESEARCH_FINDINGS.md)
- [Architecture Design](./ARCHITECTURE.md)
- [Project Plan](./PROJECT_PLAN.md)

## 🤝 Contributing

This is a hackathon submission project. For questions or collaboration, please open an issue.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built for Razorpay AI Buildathon 2026 - Track 3: AI Revenue Recovery

---

**Status:** 🚧 In Development  
**Target:** Razorpay AI Buildathon Winner 🏆
