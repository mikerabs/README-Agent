# README-Agent

A tool to enhance Python scripts and repositories with better documentation, type hints, and comprehensive README files. Now featuring OpenAI-powered README generation!

## Installation

### Python Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Basic README Generation
```bash
# Generate README for entire repository
python readme_hardener.py --repo

# Enhance a single Python script
python readme_hardener.py --script my_script.py
```

### OpenAI-Powered README Generation
```bash
# Generate README using OpenAI (requires API key)
python readme_hardener.py --repo --openai

# Generate with custom output path
python readme_hardener.py --repo --openai --out AI_README.md

# Add custom notes
python readme_hardener.py --repo --openai --notes "This is a special AI-enhanced project"
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for AI-powered README generation |
| `DATABASE_URL` | Database configuration |
| `API_KEY` | API keys |
| `DEBUG` | Application settings |
| `PORT` | Application port |

### Setting up OpenAI Integration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Generate an AI-powered README:
   ```bash
   python readme_hardener.py --repo --openai
   ```

## Running the Application

### Local Development
```bash
# View help and options
python readme_hardener.py --help

# Basic repository analysis
python readme_hardener.py --repo

# AI-enhanced README generation
python readme_hardener.py --repo --openai
```

### Docker
```bash
# Build the image
docker build -t readme-agent .

# Run the container
docker run -p 8000:8000 readme-agent
```

### Docker Compose
```bash
# Start services
docker-compose -f docker-compose.yml up -d

# Stop services
docker-compose -f docker-compose.yml down
```

## Make Targets

- `make run`
- `make install`
- `make build`
- `make clean`
- `make lint`
- `make test`

## Features

- **Script Enhancement**: Add docstrings, type hints, and argparse to Python scripts
- **Repository Analysis**: Automatically detect project structure and dependencies
- **Traditional README Generation**: Create comprehensive documentation based on project files
- **AI-Powered README Generation**: Leverage OpenAI to create intelligent, context-aware documentation
- **Docker Support**: Ready-to-use containerization setup
- **Make Integration**: Common development tasks via Makefile

## Services

This project uses Docker Compose with the following services:

See `docker-compose.yml` for service configuration.

<!-- README-HARDENER-MARKER: REPO -->
