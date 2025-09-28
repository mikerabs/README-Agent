# README-Agent

## Installation

### Python Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

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

- `make run`
- `make install`
- `make build`
- `make clean`
- `make lint`
- `make test`

## Services

This project uses Docker Compose with the following services:

See `docker-compose.yml` for service configuration.

<!-- README-HARDENER-MARKER: REPO -->
