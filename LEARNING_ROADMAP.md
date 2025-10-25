# AI Agents from Scratch - Complete Learning Roadmap

## 🎯 Your Learning Journey

This roadmap will take you from **zero to hero** in building AI agents. Follow this path step-by-step!

**Total Time**: 8-12 hours (spread over a few days)
**Difficulty**: Beginner → Intermediate → Advanced

---

## 📍 Where Are You?

Choose your starting point:

### 🟢 Complete Beginner
- **You are**: New to AI agents, maybe new to Python
- **Start with**: Tutorial 01 (30 min)
- **Goal**: Understand basics and run your first agent

### 🟡 Some Experience
- **You are**: Know Python, maybe used ChatGPT API before
- **Start with**: Tutorial 01 (review), then Tutorial 02
- **Goal**: Build agents with memory and tools

### 🔴 Advanced
- **You are**: Built simple agents, want advanced features
- **Start with**: Tutorial 03 (MCP), then Tutorial 04
- **Goal**: Build production-ready agents with complex capabilities

---

## 🗺️ The Complete Learning Path

```
START HERE
    ↓
Tutorial 01: Simple Agent (30-45 min)
    ↓
Tutorial 02: Memory (45 min)
    ↓
Tutorial 03A: Tool Integration (45 min)
    ↓
Tutorial 03B: MCP Servers (1-2 hours)
    ↓
Tutorial 04: Planning & Reasoning (60 min)
    ↓
Tutorial 05: Advanced Patterns (75-90 min)
    ↓
BUILD YOUR OWN AGENT!
```

---

## 📚 Tutorial 01: Simple Agent ⭐ START HERE

**Location**: `tutorials/01-basics/`

**What You'll Learn**:
- ✅ What an AI agent is
- ✅ How to call OpenAI API
- ✅ System prompts (agent personality)
- ✅ Message formatting
- ✅ Temperature and creativity control
- ✅ Building interactive conversations

**Time**: 30-45 minutes

**Files**:
1. **`simple_agent.py`** - The code (read this!)
2. **`LEARNING_GUIDE.md`** - Line-by-line explanation ⭐ READ THIS FIRST

**How to Start**:
```bash
cd tutorials/01-basics

# Read the learning guide
# Open: LEARNING_GUIDE.md

# Then run the agent
python simple_agent.py
```

**Exercises**:
1. Run the basic agent and chat with it
2. Create a chef agent (modify system prompt)
3. Create a translator agent
4. Experiment with temperature settings

**Success Criteria**:
- [ ] You can run the agent
- [ ] You understand system prompts
- [ ] You can modify agent personality
- [ ] You know what temperature does

**Next Step**: Tutorial 02 (Memory)

---

## 📚 Tutorial 02: Memory

**Location**: `tutorials/02-memory/`

**What You'll Learn**:
- ✅ Why agents need memory
- ✅ Conversation history
- ✅ Buffer memory (sliding window)
- ✅ Token-aware memory management
- ✅ Persistent memory (save/load)

**Time**: 45 minutes

**Files**:
1. **`agent_with_memory.py`** - Memory implementations
2. **`agent_with_memory_visualization.py`** - See memory in action!
3. **`MEMORY_EXPLAINED.md`** - How memory works

**How to Start**:
```bash
cd tutorials/02-memory

# Run the visual demo
python agent_with_memory_visualization.py

# Try the demo script
python demo_auto.py
```

**Key Concepts**:
- **Basic Memory**: Stores everything
- **Buffer Memory**: Only last N messages
- **Token Memory**: Manages by token count
- **Persistent**: Save to disk

**Exercises**:
1. Run the visualization and see memory grow
2. Test buffer memory with long conversations
3. Save and load a conversation
4. Build a summarization agent

**Success Criteria**:
- [ ] You understand why memory matters
- [ ] You can implement conversation history
- [ ] You know when to use each memory type
- [ ] You can visualize memory contents

**Next Step**: Tutorial 03A (Tool Integration)

---

## 📚 Tutorial 03A: Tool Integration

**Location**: `tutorials/03-tools/`

**What You'll Learn**:
- ✅ How and when to call tools from an agent
- ✅ Designing tool schemas and arguments
- ✅ Handling tool errors gracefully
- ✅ Logging successful and failed tool calls

**Time**: 45 minutes

**Files**:
1. **`README.md`** - Full tutorial guide
2. **`tool_agent.py`** - Reference implementation using function calling

**How to Start**:
```bash
cd tutorials/03-tools
python tool_agent.py
```

**Exercises**:
1. Add a weather lookup tool (mock the response) and update the agent prompt.
2. Implement retry logic for a flaky tool.
3. Log every tool call to a JSON file with timestamp and arguments.

**Success Criteria**:
- [ ] Understand when to favour tools vs. direct LLM answers
- [ ] Register and execute custom tools
- [ ] Handle tool errors and communicate them to the user

**Next Step**: Tutorial 03B (MCP Servers)

---

## 📚 Tutorial 03B: MCP Servers

**Location**: `tutorials/03-mcp-servers/`

**What You'll Learn**:
- ✅ What MCP (Model Context Protocol) is
- ✅ How to build MCP servers
- ✅ Tools vs Resources
- ✅ JSON-RPC protocol
- ✅ Connecting to Claude Desktop
- ✅ Testing MCP servers

**Time**: 1-2 hours

**Files**:
1. **`START_HERE.md`** - Entry point ⭐ READ FIRST
2. **`QUICKSTART.md`** - 5-minute overview
3. **`README.md`** - Complete tutorial
4. **`MCP_EXPLAINED.md`** - Deep dive
5. **`UNDERSTANDING_MCP_SERVERS.md`** - Protocol explained
6. **`simple_demo.py`** - Interactive intro
7. **`interactive_calculator.py`** - Test tools directly

**MCP Servers Included**:
1. **Calculator** (`basic/simple_mcp_server.py`) - Math operations
2. **Weather** (`tools/weather_mcp_server.py`) - Weather service
3. **File Explorer** (`resources/file_explorer_server.py`) - File access

**How to Start**:
```bash
cd tutorials/03-mcp-servers

# Step 1: Run simple demo
python simple_demo.py

# Step 2: Try interactive calculator
python interactive_calculator.py

# Step 3: Read START_HERE.md
```

**Exercises**:
1. Run the interactive calculator
2. Modify calculator to add subtraction
3. Create your own MCP server
4. Connect to Claude Desktop

**Success Criteria**:
- [ ] You understand MCP protocol
- [ ] You can build MCP servers
- [ ] You know difference between tools and resources
- [ ] You've connected to Claude Desktop (optional)

**Next Step**: Tutorial 04 (Planning & Reasoning)

---

## 📚 Tutorial 04: Planning & Reasoning

**Location**: `tutorials/04-planning/`

**What You'll Learn**:
- ✅ Why agents benefit from planning loops
- ✅ Implementing the ReAct pattern with custom prompts
- ✅ Task decomposition with heuristics or LLM assistance
- ✅ Combining planning with memory and tool calls

**Time**: 60 minutes

**Files**:
1. **`README.md`** - Conceptual guide, prompts, and troubleshooting
2. **`planning_agent.py`** - Full ReAct + decomposition example

**How to Start**:
```bash
cd tutorials/04-planning
python planning_agent.py
```

**Exercises**:
1. Add a new tool (e.g., knowledge base search) and update the planner prompt.
2. Capture the Thought/Action/Observation trajectory to a Markdown log.
3. Experiment with different `max_steps` limits and analyze the effect.

**Success Criteria**:
- [ ] Understand the ReAct reasoning loop
- [ ] Build prompts that encourage tool usage
- [ ] Decompose a complex goal into actionable subtasks

**Next Step**: Tutorial 05 (Advanced Patterns)

---

## 📚 Tutorial 05: Advanced Patterns

**Location**: `tutorials/05-advanced/`

**What You'll Learn**:
- ✅ Retrieval-Augmented Generation (RAG) with a lightweight vector store
- ✅ Coordinating specialized agents in a team structure
- ✅ Requesting and applying self-evaluation feedback
- ✅ Designing revision loops with clear stopping criteria

**Time**: 75-90 minutes

**Files**:
1. **`README.md`** - High-level guidance and exercises
2. **`rag_agent.py`** - Minimal RAG implementation
3. **`multi_agent_team.py`** - Manager/worker/reviewer orchestration

**How to Start**:
```bash
cd tutorials/05-advanced
python rag_agent.py        # Explore retrieval
python multi_agent_team.py # Try collaborative workflow
```

**Exercises**:
1. Index your own notes or documentation in the vector store.
2. Add a new specialist agent (e.g., visualization or QA) to the team.
3. Persist reviewer feedback to a Markdown or JSON file for audits.

**Success Criteria**:
- [ ] Retrieve and use contextual documents during generation
- [ ] Orchestrate multiple agents with different strengths
- [ ] Apply reviewer feedback to improve a draft

**Next Step**: Build a project or revisit earlier tutorials for mastery

---

## 🎓 Learning Tips

### 1. **Don't Skip Ahead**
Each tutorial builds on the previous one. Take your time!

### 2. **Type the Code**
Don't just read - type it out. You'll learn better!

### 3. **Break Things**
Try modifying the code. See what breaks. Learn from errors!

### 4. **Take Notes**
Keep a learning journal. Write down key concepts.

### 5. **Build Projects**
After each tutorial, build something with what you learned!

---

## 🛠️ Setup (Do This First!)

### Step 1: Prerequisites

**Install Python 3.8+**:
```bash
python --version  # Should be 3.8 or higher
```

**Create Virtual Environment**:
```bash
cd "c:\Users\Niket Sharma\llmapp\AI-Agents-from-scratch"
python -m venv venv
venv\Scripts\activate
```

**Install Dependencies**:
```bash
pip install -r requirements.txt
```

### Step 2: Get API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up / Log in
3. Go to API Keys
4. Create new secret key
5. Copy it!

### Step 3: Setup `.env` File

Create `.env` in project root:
```
OPENAI_API_KEY=sk-your-key-here
```

**Security Note**: Never commit `.env` to git! It's already in `.gitignore`.

### Step 4: Test Setup

```bash
python -c "from openai import OpenAI; import os; from dotenv import load_dotenv; load_dotenv(); print('Setup OK!' if os.getenv('OPENAI_API_KEY') else 'Missing API key!')"
```

Should print: `Setup OK!`

---

## 📖 Recommended Daily Plan

### Day 1: Foundations (1-2 hours)
- ✅ Setup environment
- ✅ Read Tutorial 01 LEARNING_GUIDE.md
- ✅ Run simple_agent.py
- ✅ Complete Tutorial 01 exercises
- ✅ Build a custom agent (chef, tutor, etc.)

### Day 2: Memory (1-2 hours)
- ✅ Read memory concepts
- ✅ Run visualization demos
- ✅ Test different memory types
- ✅ Complete Tutorial 02 exercises
- ✅ Build an agent that remembers conversations

### Day 3: Tool Integration (1 hour)
- ✅ Read `tutorials/03-tools/README.md`
- ✅ Run `tool_agent.py`
- ✅ Register an additional tool and test it

### Day 4: MCP Basics (1-2 hours)
- ✅ Read `START_HERE.md`
- ✅ Run `simple_demo.py`
- ✅ Try `interactive_calculator.py`
- ✅ Read `UNDERSTANDING_MCP_SERVERS.md`

### Day 5: Planning & Reasoning (1-2 hours)
- ✅ Read `tutorials/04-planning/README.md`
- ✅ Run `planning_agent.py`
- ✅ Capture a ReAct trajectory and analyze it

### Day 6: Advanced Patterns (2 hours)
- ✅ Explore `rag_agent.py`
- ✅ Run `multi_agent_team.py`
- ✅ Customize the retrieval store or add a new agent

### Day 7: Build Your Own! (2-4 hours)
- ✅ Design your own agent
- ✅ Implement features you learned
- ✅ Test thoroughly
- ✅ Share your creation!

---

## 🎯 Project Ideas by Skill Level

### Beginner Projects

**1. Personality Chat Bots**
- Build different character bots (pirate, chef, teacher)
- Use different system prompts
- Practice API basics

**2. Simple Q&A Agent**
- Answer questions on a specific topic
- Use appropriate temperature
- Add personality

**3. Language Practice Bot**
- Help users practice a foreign language
- Provide corrections
- Encourage practice

### Intermediate Projects

**4. Note-Taking Assistant**
- Remember conversation history
- Summarize discussions
- Save notes to files

**5. Code Helper**
- Answer Python questions
- Explain code concepts
- Provide examples

**6. Study Buddy**
- Quiz user on topics
- Remember what was studied
- Track progress

### Advanced Projects

**7. Personal Assistant**
- Calendar integration (MCP server)
- Email access
- Task management

**8. Research Assistant**
- Search and summarize articles
- Save findings
- Generate reports

**9. Code Review Agent**
- Analyze code files (MCP resources)
- Provide suggestions
- Check best practices

---

## 📊 Progress Tracker

Use this to track your learning:

### Tutorial 01: Simple Agent
- [ ] Read LEARNING_GUIDE.md
- [ ] Run simple_agent.py
- [ ] Create custom system prompt
- [ ] Understand temperature
- [ ] Complete all exercises
- [ ] Build own agent

### Tutorial 02: Memory
- [ ] Understand memory types
- [ ] Run visualization
- [ ] Test buffer memory
- [ ] Save/load conversations
- [ ] Complete exercises
- [ ] Build memory-enabled agent

### Tutorial 03: MCP Servers
- [ ] Read START_HERE.md
- [ ] Run simple_demo.py
- [ ] Try interactive_calculator.py
- [ ] Understand JSON-RPC
- [ ] Study 3 server examples
- [ ] Build own MCP server
- [ ] (Optional) Connect to Claude Desktop

---

## 🆘 Getting Help

### Common Issues

**"ModuleNotFoundError"**
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

**"OPENAI_API_KEY not found"**
- Check `.env` file exists
- Check API key format (should start with `sk-`)
- Make sure `.env` is in correct location

**"AuthenticationError"**
- Check API key is correct
- Check you have credits on OpenAI account

**"Path with spaces error"**
- Use quotes: `cd "c:\Users\Niket Sharma\path"`
- Or use batch files provided

### Resources

- **OpenAI Docs**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **Python Docs**: [docs.python.org](https://docs.python.org)
- **MCP Spec**: [modelcontextprotocol.io](https://modelcontextprotocol.io)

---

## 🎉 Completion Checklist

After completing all tutorials:

- [ ] I can build a basic AI agent
- [ ] I can implement conversation memory
- [ ] I can build MCP servers
- [ ] I understand tools vs resources
- [ ] I can connect agents to external systems
- [ ] I've built my own custom agent
- [ ] I'm ready to build production agents!

---

## 🚀 Next Steps After Tutorials

### 1. Build Real Projects
Apply what you learned to solve real problems!

### 2. Study Advanced Topics
- RAG (Retrieval-Augmented Generation)
- Multi-agent systems
- LangChain / LlamaIndex
- Agent evaluation and testing

### 3. Join Community
- Share your projects
- Help others learn
- Contribute to open source

### 4. Stay Updated
- Follow AI agent developments
- Try new models and techniques
- Experiment with latest features

---

## 📝 Summary

**You're about to learn**:
1. How to build AI agents from scratch
2. How to give agents memory
3. How to connect agents to tools (MCP)
4. How to build production-ready systems

**Start here**: `tutorials/01-basics/LEARNING_GUIDE.md`

**Time investment**: 8-12 hours total

**Outcome**: You'll be able to build sophisticated AI agents!

---

**Ready to begin? Open `tutorials/01-basics/LEARNING_GUIDE.md` and let's start coding!** 🎯
