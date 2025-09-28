# README-Agent

A comprehensive Python CLI tool for enhancing scripts with documentation and generating repository READMEs.

## Installation

### Python Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### CLI Usage Examples

```bash
# Show help
python readme_hardener.py --help

# Enhance a single Python script
python readme_hardener.py --script my_script.py

# Generate README for entire repository
python readme_hardener.py --repo

# Specify custom output location
python readme_hardener.py --repo --out README_new.md

# Add custom notes
python readme_hardener.py --repo --notes "This is a special project"

# Load notes from file
python readme_hardener.py --repo --notes-file notes.txt

# Run with verification (requires black/ruff)
python readme_hardener.py --script my_script.py --verify
```

### Local Development
```bash
# Run your main Python script
python <script_name>.py
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

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Database configuration |
| `API_KEY` | API keys |
| `DEBUG` | Application settings |
| `PORT` | No description |

## Make Targets

- `make clean`
- `make lint`
- `make test`
- `make run`
- `make build`
- `make install`

## Services

This project uses Docker Compose with the following services:

See `docker-compose.yml` for service configuration.

<!-- README-HARDENER-MARKER: REPO -->
