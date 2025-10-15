# Quick Start Guide

Get up and running with AI Agents in 5 minutes!

## Step 1: Prerequisites

Ensure you have:
- Python 3.8 or higher
- An OpenAI or Anthropic API key ([Get OpenAI key](https://platform.openai.com/api-keys))

## Step 2: Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/AI-Agents-from-scratch.git
cd AI-Agents-from-scratch

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
# On Windows, you can use: notepad .env
# On macOS/Linux: nano .env
```

Add your API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Step 4: Run Your First Agent!

### Option A: Basic Agent

```bash
python tutorials/01-basics/simple_agent.py
```

Try asking:
- "What is Python?"
- "Explain AI agents in simple terms"
- Type 'quit' to exit

### Option B: Agent with Memory

```bash
python tutorials/02-memory/agent_with_memory.py
```

Try:
- "My name is Alice"
- "What's my name?"
- "I like Python programming"
- "What do I like?"

### Option C: Agent with Tools

```bash
python tutorials/03-tools/tool_agent.py
```

Try:
- "What's 1234 multiplied by 5678?"
- "What's the weather in Tokyo?"
- "What time is it in UTC?"

## Step 5: Explore Tutorials

Work through the tutorials in order:

1. **[Tutorial 01: Basic Agent](tutorials/01-basics/)** (30 min)
   - Build your first conversational agent

2. **[Tutorial 02: Memory](tutorials/02-memory/)** (45 min)
   - Add conversation memory

3. **[Tutorial 03: Tools](tutorials/03-tools/)** (1 hour)
   - Enable tool use and function calling

4. **Tutorial 04: Planning** (Coming soon)
   - Implement reasoning and planning

5. **Tutorial 05: Advanced** (Coming soon)
   - Multi-agent systems and RAG

## Common Issues

### "API key not found"

**Solution**:
1. Make sure `.env` file exists in the project root
2. Check that it contains: `OPENAI_API_KEY=your-key-here`
3. No quotes around the key

### "Module not found"

**Solution**:
```bash
# Make sure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt
```

### "Rate limit exceeded"

**Solution**: You're making too many requests. Wait a minute and try again.

## Next Steps

- **Learn the Concepts**: Read [docs/concepts.md](docs/concepts.md)
- **Understand Architecture**: Check [docs/architecture.md](docs/architecture.md)
- **Build Examples**: Explore [examples/](examples/) directory
- **Customize**: Modify the agents to suit your needs

## Quick Code Example

```python
from tutorials.basics.simple_agent import SimpleAgent

# Create an agent
agent = SimpleAgent(
    model="gpt-3.5-turbo",
    system_prompt="You are a helpful Python tutor."
)

# Get a response
response = agent.generate_response("What is a function?")
print(response)
```

## Tips for Learning

1. **Start Simple**: Begin with Tutorial 01
2. **Experiment**: Modify the code and see what happens
3. **Read Comments**: Code examples include detailed comments
4. **Use Notebooks**: Interactive Jupyter notebooks available
5. **Check Docs**: Comprehensive documentation in `docs/`

## Getting Help

- **Issues**: Report bugs or ask questions via [GitHub Issues](https://github.com/yourusername/AI-Agents-from-scratch/issues)
- **Documentation**: Check the [docs](docs/) folder
- **Examples**: Look at working examples in [examples](examples/)

## What's an AI Agent?

An AI agent is more than a chatbot - it can:
- **Remember** past conversations
- **Use tools** to access external information
- **Plan** multi-step tasks
- **Reason** through complex problems

Example:
```
User: "Find restaurants near me, check reviews, and book a table"

Chatbot: "I can't do that"

Agent:
1. [Uses location tool]
2. [Searches for restaurants]
3. [Checks review APIs]
4. [Presents options]
5. [Books reservation when confirmed]
```

## Resources

- **Core Concepts**: [docs/concepts.md](docs/concepts.md)
- **API Documentation**:
  - [OpenAI](https://platform.openai.com/docs)
  - [Anthropic](https://docs.anthropic.com)
- **Community**: [GitHub Discussions](https://github.com/yourusername/AI-Agents-from-scratch/discussions)

---

**Happy building!** Start with [Tutorial 01](tutorials/01-basics/) and work your way through. Each tutorial builds on the previous one.
