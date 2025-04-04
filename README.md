# The Shill Game

A Web3-based AI agent game platform built with Next.js and Python.

## Project Overview

The Shill Game is a Web3-based AI agent gaming platform where players can interact and compete with AI agents.

## Tech Stack

### Frontend
- Next.js 15.2
- React 19
- TypeScript
- TailwindCSS
- RainbowKit (Web3 integration)
- Wagmi (Ethereum interactions)
- Pixel RetroUI (UI components)

### Backend
- Python 3.12+
- Poetry (dependency management)
- OpenAI Agents
- Ruff (linting)

## Project Structure

```
.
├── frontend/           # Next.js frontend application
│   ├── src/           # Source code
│   ├── public/        # Static assets
│   └── ...           # Configuration files
│
└── backend/           # Python backend service
    ├── src/          # Source code
    └── tests/        # Test files
```

## Getting Started

### Frontend Setup

```bash
cd frontend
bun install
bun run dev
```

### Backend Setup

```bash
cd backend
poetry install
poetry run python -m src.main
```

## Contributing

Pull Requests and Issues are welcome!

## License

[MIT License](LICENSE)
