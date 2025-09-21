# Multi-Agent NORA System 🤖

A comprehensive multi-agent AI system for managing Cisco Intersight operations and Service Catalog interactions. The system features intelligent routing through a supervisor agent and provides both API and CLI interfaces.

## 🏗️ System Architecture

### Agents

1. **🔧 Cisco Intersight Agent** (Port 8002)

   - Handles Cisco Intersight operations and greetings
   - Provides device management and policy configuration
   - Endpoint: `http://localhost:8002`

2. **📋 Service Catalog Agent** (Port 8001)

   - Manages service catalog operations and inquiries
   - Provides service discovery and catalog browsing
   - Endpoint: `http://localhost:8001`

3. **🎯 Supervisor Agent** (Port 8000)
   - Routes requests to appropriate specialized agents
   - Provides intelligent coordination between agents
   - Endpoint: `http://localhost:8000`

### Components

- **CLI Client**: Rich interactive command-line interface
- **API Servers**: RESTful APIs for each agent
- **Configuration Management**: Environment-based configuration
- **LLM Integration**: OpenAI GPT-3.5-turbo support

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- UV package manager (recommended) or pip
- OpenAI API key

### Installation

1. **Clone and navigate to the project:**

   ```bash
   cd /path/to/multi-agent-nora
   ```

2. **Set up environment:**

   ```bash
   # Install dependencies
   uv sync

   # Or with pip
   pip install -e .
   ```

3. **Configure environment variables:**

   ```bash
   # Copy and edit .env file
   cp .env.example .env

   # Add your OpenAI API key
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

## 🎮 Usage

### Method 1: All-in-One Launcher (Recommended)

```bash
# Start all agents
python main.py start

# Start a specific agent
python main.py start-agent --agent cisco
python main.py start-agent --agent service-catalog
python main.py start-agent --agent supervisor

# Check system status
python main.py status

# Get system information
python main.py info

# Launch CLI directly
python main.py cli
```

### Method 2: Individual Agent Startup

```bash
# Start Cisco Intersight Agent
python -m agents.cisco_intersight.server

# Start Service Catalog Agent
python -m agents.service_catalog.server

# Start Supervisor Agent
python -m agents.supervisor.main
```

### Method 3: CLI Client Usage

```bash
# Interactive CLI
python -m client.cli

# Send a single message
python -m client.cli chat "Hello, how can you help me?"

# Send to specific agent
python -m client.cli chat "Show me Cisco devices" --agent cisco

# Interactive mode
python -m client.cli interactive

# Check agent status
python -m client.cli status

# Broadcast to multiple agents
python -m client.cli broadcast "Hello everyone" --all-agents

# Get agent information
python -m client.cli info
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key

# Optional (with defaults)
LLM_PROVIDER=openai
DEFAULT_MESSAGE_TRANSPORT=nats
TRANSPORT_SERVER=nats://localhost:4222
SERVICE_CATALOG_AGENT_URL=http://localhost:8001
CISCO_INTERSIGHT_AGENT_URL=http://localhost:8002
```

### Agent Ports

- **Cisco Intersight**: 8002
- **Service Catalog**: 8001
- **Supervisor**: 8000

## 🎯 Examples

### Basic Interactions

```bash
# 1. Start the system
python main.py start

# 2. In another terminal, interact via CLI
python -m client.cli interactive

# 3. Try these sample messages:
# "Hello, can you help me with Cisco devices?"
# "What services are available in the catalog?"
# "I need information about network policies"
```

### API Examples

```bash
# Direct API call to Cisco agent
curl -X POST http://localhost:8002/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test_call",
    "params": {
      "message": {
        "message_id": "test_1",
        "role": "user",
        "parts": [{"text": "Hello Cisco agent!"}]
      }
    }
  }'

# Supervisor agent call
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Route this to the appropriate agent"}'
```

### CLI Interactive Mode

```bash
python -m client.cli interactive

# Commands in interactive mode:
# - Type messages to send to agents
# - 'switch' - Change current agent
# - 'status' - Check agent status
# - 'help' - Show available commands
# - 'exit' - Quit the session
```

## 🔍 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**:

   ```bash
   # Ensure you're running from project root
   cd /path/to/multi-agent-nora

   # Install dependencies
   uv sync
   ```

2. **Connection refused**:

   ```bash
   # Check if agents are running
   python main.py status

   # Start agents if not running
   python main.py start
   ```

3. **API Key errors**:

   ```bash
   # Verify .env file has correct API key
   cat .env | grep OPENAI_API_KEY
   ```

4. **Port conflicts**:

   ```bash
   # Check what's using the ports
   netstat -an | findstr ":8000 :8001 :8002"

   # Kill existing processes if needed
   taskkill /F /PID <process_id>
   ```

### Debug Mode

```bash
# Enable verbose logging
python -m client.cli -v status

# Check individual agent health
curl http://localhost:8002/health  # Cisco
curl http://localhost:8001/health  # Service Catalog
curl http://localhost:8000/docs    # Supervisor
```

### Logs

Each agent outputs logs to the console. Look for:

- `INFO:root:Starting [Agent] Server...` - Successful startup
- `INFO:     Uvicorn running on http://...` - Server ready
- Error messages in red for troubleshooting

## 🛠️ Development

### Project Structure

```
multi-agent-nora/
├── agents/                    # Agent implementations
│   ├── cisco_intersight/     # Cisco agent
│   ├── service_catalog/      # Service catalog agent
│   ├── supervisor/           # Supervisor agent
│   └── templates/            # Agent templates
├── client/                   # CLI client
├── common/                   # Shared utilities
├── config/                   # Configuration
├── mcpServers/              # MCP server implementations
├── main.py                  # System launcher
├── pyproject.toml           # Dependencies
└── README.md               # This file
```

### Adding New Agents

1. Copy the template files from `agents/templates/`
2. Implement your agent logic
3. Add the new agent to the system launcher
4. Update CLI client with new agent endpoint

### Testing

```bash
# Test individual components
python -m agents.cisco_intersight.server
python -m agents.service_catalog.server
python -m agents.supervisor.main

# Test CLI
python -m client.cli --help

# Test system launcher
python main.py info
```

## 📚 API Documentation

### A2A Agent API

Each specialized agent (Cisco, Service Catalog) uses the A2A protocol:

**Endpoint**: `POST /{agent_url}/v1/messages`

**Request**:

```json
{
  "id": "unique_request_id",
  "params": {
    "message": {
      "message_id": "unique_message_id",
      "role": "user",
      "parts": [{ "text": "Your message here" }]
    }
  }
}
```

**Response**:

```json
{
  "message": {
    "message_id": "response_id",
    "role": "agent",
    "parts": [{ "text": "Agent response" }],
    "metadata": { "name": "Agent Name" }
  }
}
```

### Supervisor API

**Endpoint**: `POST /agent/chat`

**Request**:

```json
{
  "message": "Your message here"
}
```

**Response**:

```json
{
  "response": "Agent response"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Your License Here]

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review logs for error messages
3. Ensure all dependencies are installed
4. Verify environment configuration

---

**Happy agent orchestration! 🚀**
# multi-agent-ai-with-a2a
