<div align="center">
  <br/>
  <img src="https://img.shields.io/badge/status-active-success" alt="Status"/>
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License"/>
  <img src="https://img.shields.io/badge/python-3.11+-green" alt="Python"/>
  <img src="https://img.shields.io/badge/fastapi-0.104+-blueviolet" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/next.js-14-black" alt="Next.js"/>
  <br/>
  <br/>
</div>

# AI Negotiation Arena

> **Where autonomous AI agents learn to compete, cooperate, betray, and survive.**

<br/>

A real-time multi-agent simulation platform where AI agents interact in game-theoretic environments. Watch as agents negotiate resources, form alliances, betray each other, adapt their strategies, and evolve — all visualized in a live, interactive dashboard.

<br/>

## ✨ Features

### 🧠 Multi-Agent AI System
- **8 Agent Strategies**: From classic (Tit-for-Tat, Grim Trigger) to adaptive (personality-driven strategies)
- **Personality System**: Each agent has unique traits (trust, greed, forgiveness, reciprocity, spite)
- **Memory System**: Agents remember past interactions and build opponent models
- **Real-time Decision Making**: Async agents making strategic choices every tick

### 🎮 Game Theory Engine
- **Prisoner's Dilemma**: The classic strategic game with full payoff matrix implementation
- **Multiple Game Types**: Prisoner's Dilemma, Chicken, Stag Hunt (extensible)
- **Nash Equilibrium Computation**: Pure strategy equilibrium finder
- **Tournament Systems**: Round-robin, random pairs, Swiss system, elimination

### ⚡ Real-time Architecture
- **WebSocket Protocol**: Live streaming of all simulation events
- **Concurrent Simulation Loop**: Async event-driven engine
- **Speed Controls**: Adjust simulation speed from 0.1x to 10x
- **Pause/Resume**: Full lifecycle management

### 📊 Interactive Dashboard
- **Live Leaderboard**: Real-time standings with score bars
- **Cooperation Chart**: Track cooperation rates over time
- **Strategy Distribution**: See which strategies dominate
- **Event Log**: Scrolling feed of all match results
- **Agent Explorer**: Detailed view of each agent's behavior

<br/>

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │   Dashboard  │ │    Agent     │ │  Analytics   ││
│  │   Overview   │ │   Explorer   │ │    Page      ││
│  └──────────────┘ └──────────────┘ └──────────────┘│
│         ▲              ▲               ▲           │
│         │         WebSocket (ws://)      │           │
│         └──────────────┼───────────────┘           │
└────────────────────────┼───────────────────────────┘
                         │
┌────────────────────────┼───────────────────────────┐
│               Backend (FastAPI)                     │
│  ┌─────────────────────┴──────────────────────┐    │
│  │           WebSocket Manager                │    │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────────┐ │    │
│  │  │  Room   │ │  Event  │ │  Broadcast   │ │    │
│  │  │ Manager │ │   Bus   │ │   Handler    │ │    │
│  │  └─────────┘ └─────────┘ └──────────────┘ │    │
│  └──────────────────┬─────────────────────────┘    │
│                     │                               │
│  ┌──────────────────┴─────────────────────────┐    │
│  │           Simulation Engine                 │    │
│  │  ┌──────────┐ ┌──────────┐ ┌────────────┐ │    │
│  │  │  Match   │ │  Agent   │ │  Game      │ │    │
│  │  │  Maker   │ │  Executor│ │  Logic     │ │    │
│  │  └──────────┘ └──────────┘ └────────────┘ │    │
│  └──────────────────┬─────────────────────────┘    │
│                     │                               │
│  ┌──────────────────┴─────────────────────────┐    │
│  │            Database (PostgreSQL)            │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

<br/>

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)

### Using Docker (Recommended)

```bash
git clone https://github.com/yourname/ai-negotiation-arena.git
cd ai-negotiation-arena
make docker-up
# Open http://localhost:3000
```

### Manual Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

<br/>

## 🧪 Running Tests

```bash
make test        # Run all tests
make test-watch  # Run tests in watch mode
```

<br/>

## 🗺 Project Structure

```
ai-negotiation-arena/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Settings
│   │   ├── api/                    # REST endpoints
│   │   ├── core/                   # Simulation engine, event bus
│   │   ├── agents/                 # Agent strategies, memory, personality
│   │   ├── games/                  # Game theory implementations
│   │   ├── websocket/              # WebSocket manager
│   │   └── database/               # SQLAlchemy models
│   └── tests/                      # Pytest test suite
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js pages
│   │   ├── components/             # React components
│   │   ├── hooks/                  # Custom hooks
│   │   └── lib/                    # Types, API client
│   └── package.json
├── docker-compose.yml
├── Makefile
└── README.md
```

<br/>

## 🧠 Agent Strategies

| Strategy | Type | Description |
|---|---|---|
| **Always Cooperate** | Classic | Cooperates unconditionally |
| **Always Defect** | Classic | Defects unconditionally |
| **Tit-for-Tat** | Classic | Mirrors opponent's last move |
| **Grim Trigger** | Reactive | Cooperates until betrayed, then defects forever |
| **Pavlov** | Adaptive | Win-stay, lose-shift |
| **Generous TFT** | Forgiving | TFT with occasional forgiveness |
| **Random** | Stochastic | Random choice |
| **Adaptive** | Personality-driven | Uses trust, greed, forgiveness traits |

<br/>

## 📊 API Endpoints

### REST
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/strategies` | List available strategies |
| `POST` | `/api/simulations` | Create and start simulation |
| `GET` | `/api/simulations` | List simulations |
| `GET` | `/api/simulations/{id}` | Get simulation state |
| `GET` | `/api/simulations/{id}/standings` | Get tournament standings |
| `GET` | `/api/simulations/{id}/agents` | Get agent details |
| `POST` | `/api/simulations/{id}/actions` | Pause/resume/stop |

### WebSocket
| Endpoint | Description |
|---|---|
| `/ws` | Create new simulation room |
| `/ws/{simulation_id}` | Connect to existing simulation |

<br/>

## 🔬 Research Inspiration

This project builds on foundational work in:

- **Robert Axelrod** — *The Evolution of Cooperation* (1984)
- **Martin Nowak** — *Evolutionary Dynamics* (2006)
- **Sutton & Barto** — *Reinforcement Learning: An Introduction* (2018)
- **John Nash** — Equilibrium theory in non-cooperative games (1950)

<br/>

## 🗺 Roadmap

### Phase 1 — MVP (Current)
- [x] Prisoner's Dilemma game engine
- [x] 8 agent strategies
- [x] Real-time WebSocket simulation
- [x] Interactive dashboard
- [x] REST API

### Phase 2 — Enhanced AI
- [ ] Q-Learning agents
- [ ] Opponent modeling
- [ ] DQN integration with Stable-Baselines3
- [ ] Evolutionary strategy optimization

### Phase 3 — Complex Games
- [ ] Ultimatum game
- [ ] Auctions (English, Dutch, Vickrey)
- [ ] Public goods game
- [ ] Coalition formation

### Phase 4 — Blockchain & LLMs
- [ ] On-chain settlement
- [ ] Token economy integration
- [ ] LLM-powered natural language negotiation
- [ ] DAO governance simulation

### Phase 5 — Autonomous Societies
- [ ] Resource economies
- [ ] Cultural evolution
- [ ] Agent specialization
- [ ] Large-scale simulations (1000+ agents)

<br/>

## 🤝 Contributing

Contributions are welcome! This is an educational project designed to be extended. 

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

<br/>

## 📄 License

MIT

<br/>

---

<div align="center">
  <sub>Built with ❤️ for the future of multi-agent AI systems</sub>
</div>
