# Building AI Agents from Scratch: A Comprehensive Tutorial

A step-by-step guide to building intelligent AI agents from the ground up. Learn core concepts, implementation patterns, and best practices through hands-on tutorials.

## What You'll Learn

- **Fundamentals**: Understand what AI agents are and how they differ from simple chatbots
- **Memory Systems**: Implement short-term and long-term memory for contextual conversations
- **Tool Integration**: Enable agents to interact with external systems and APIs
- **Planning & Reasoning**: Build agents that can break down complex tasks and reason through problems
- **Advanced Patterns**: Create multi-agent systems, implement RAG, and build specialized agent teams

## Prerequisites

- Python 3.8 or higher
- Basic understanding of Python programming
- Familiarity with APIs and JSON
- OpenAI or Anthropic API key (free tier is sufficient for tutorials)
- Basic understanding of machine learning concepts (helpful but not required)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/AI-Agents-from-scratch.git
cd AI-Agents-from-scratch

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Run Your First Agent

```bash
# Run the basic agent example
python tutorials/01-basics/simple_agent.py
```

## Table of Contents

### Documentation
- [Core Concepts](docs/concepts.md) - Understand AI agent fundamentals
- [Architecture Overview](docs/architecture.md) - System design and patterns
- [Learning Resources](docs/resources.md) - Curated resources for deeper learning

### Tutorials

#### [Tutorial 01: Basic Agent](tutorials/01-basics/)
Build your first AI agent with a simple conversation loop
- Set up API connections
- Create a basic agent class
- Implement prompt-response cycles
- **Time**: 30 minutes

#### [Tutorial 02: Adding Memory](tutorials/02-memory/)
Give your agent the ability to remember past conversations
- Implement conversation history
- Create memory buffers
- Add memory summarization
- **Time**: 45 minutes

#### [Tutorial 03: MCP Servers](tutorials/03-mcp-servers/)
Build Model Context Protocol (MCP) servers from scratch
- Understand MCP architecture (servers, clients, tools, resources)
- Create basic MCP server with calculator tools
- Build advanced tools (weather service with multiple endpoints)
- Expose resources (file system access)
- Test servers with custom MCP client
- Connect to Claude Desktop
- **Time**: 1-2 hours

#### [Tutorial 04: Tool Integration](tutorials/04-tools/)
Enable your agent to use external tools and APIs
- Define tool schemas
- Implement function calling
- Add error handling
- Create custom tools
- **Time**: 1 hour

#### [Tutorial 05: Planning and Reasoning](tutorials/05-planning/)
Build agents that can think through complex problems
- Implement ReAct pattern
- Add multi-step planning
- Create task decomposition
- **Time**: 1 hour

#### [Tutorial 06: Advanced Features](tutorials/06-advanced/)
Master advanced agent capabilities
- Vector database integration
- Retrieval-Augmented Generation (RAG)
- Multi-agent systems
- Streaming responses
- **Time**: 1.5 hours

### Example Applications

Real-world agent implementations you can use as templates:
- [Customer Support Agent](examples/customer_support_agent.py)
- [Code Assistant Agent](examples/code_assistant_agent.py)
- [Research Agent](examples/research_agent.py)
- [Data Analysis Agent](examples/data_analysis_agent.py)

## Project Structure

```
AI-Agents-from-scratch/
├── docs/                 # Conceptual documentation
├── tutorials/            # Step-by-step tutorials
│   ├── 01-basics/
│   ├── 02-memory/
│   ├── 03-mcp-servers/  # NEW: MCP server tutorials
│   ├── 04-tools/
│   ├── 05-planning/
│   └── 06-advanced/
├── src/                  # Reusable agent framework
│   ├── agent/           # Core agent classes
│   ├── memory/          # Memory implementations
│   ├── tools/           # Tool management
│   └── utils/           # Helper utilities
├── examples/            # Example applications
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
└── setup.py            # Package installation
```

## Key Features

- **Progressive Learning**: Start simple, gradually add complexity
- **Hands-on Approach**: Every concept includes working code
- **Interactive Notebooks**: Jupyter notebooks for experimentation
- **Production-Ready**: Learn patterns used in real applications
- **Multiple LLM Providers**: Works with OpenAI, Anthropic, and more
- **Comprehensive Tests**: Learn testing strategies for AI systems

## Learning Path

1. **Beginners**: Follow tutorials 01-03 sequentially
2. **Intermediate**: Skip to tutorial 03 or 04
3. **Advanced**: Explore tutorial 05 and example applications
4. **Framework Builders**: Study the `src/` directory for reusable components

## Technologies Used

- **LLM APIs**: OpenAI GPT-4, Anthropic Claude
- **Frameworks**: LangChain (optional), custom implementations
- **Vector Databases**: ChromaDB for embeddings
- **Testing**: pytest for unit tests
- **UI**: Gradio for interactive demos (optional)

## Requirements

See [requirements.txt](requirements.txt) for a complete list. Core dependencies:

```
openai>=1.0.0
anthropic>=0.8.0
python-dotenv>=1.0.0
requests>=2.31.0
```

## Contributing

We welcome contributions! Whether it's:
- Fixing typos or bugs
- Adding new tutorials
- Improving documentation
- Sharing your agent implementations

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## FAQ

**Q: Do I need a paid API key?**
A: Free tier APIs from OpenAI or Anthropic are sufficient for all tutorials.

**Q: Can I use other LLM providers?**
A: Yes! The framework is designed to be provider-agnostic. See the LLM interface documentation.

**Q: Is this suitable for production use?**
A: The tutorials teach production-ready patterns, but you should add proper error handling, monitoring, and security for production deployments.

**Q: How is this different from LangChain?**
A: We build from scratch to teach fundamentals. You'll understand what frameworks like LangChain do under the hood.

## Troubleshooting

- **API Key Issues**: Make sure your `.env` file is properly configured
- **Import Errors**: Activate your virtual environment and reinstall dependencies
- **Rate Limits**: Use free tier APIs responsibly; add delays between requests

See [docs/troubleshooting.md](docs/troubleshooting.md) for more help.

## Roadmap

- [ ] Tutorial 06: Agent Evaluation and Testing
- [ ] Tutorial 07: Production Deployment
- [ ] Video tutorial series
- [ ] Interactive web-based tutorials
- [ ] Support for open-source LLMs (Llama, Mistral)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

This project is inspired by the growing AI agent ecosystem and aims to make agent development accessible to everyone.

## Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/yourusername/AI-Agents-from-scratch/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/yourusername/AI-Agents-from-scratch/discussions)
- **Twitter**: Follow updates [@yourusername](https://twitter.com/yourusername)

---

**Start your journey**: [Tutorial 01 - Basic Agent](tutorials/01-basics/)
