# 🎓 Start Learning AI Agents Here!

## Welcome! You're in the Right Place 👋

This guide will teach you how to build AI agents from scratch, step by step, line by line.

**No prior AI experience needed!** Just basic Python knowledge.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Check Your Setup

```bash
# Make sure you're in the project folder
cd "c:\Users\Niket Sharma\llmapp\AI-Agents-from-scratch"

# Activate virtual environment
venv\Scripts\activate

# Verify setup
python -c "import openai; from dotenv import load_dotenv; print('Setup OK!')"
```

**If you get an error**, see [LEARNING_ROADMAP.md](LEARNING_ROADMAP.md#setup-do-this-first) for setup instructions.

### Step 2: Run Your First Agent

```bash
cd tutorials\01-basics
python simple_agent.py
```

Try asking:
- "What is Python?"
- "Tell me a joke"
- "Explain AI in one sentence"

Type `quit` to exit.

### Step 3: Understand How It Works

Open and read:
```
tutorials/01-basics/LEARNING_GUIDE.md
```

This explains **every single line** of code!

---

## 📖 Your Learning Path

```
Day 1: Tutorial 01 - Simple Agent (30-45 min)
   ↓
Day 2: Tutorial 02 - Memory (45 min)
   ↓
Day 3: Tutorial 03A - Tool Integration (45 min)
   ↓
Day 4: Tutorial 03B - MCP Servers (1-2 hours)
   ↓
Day 5: Tutorial 04 - Planning & Reasoning (60 min)
   ↓
Day 6: Tutorial 05 - Advanced Patterns (75-90 min)
   ↓
Build Your Own Agent!
```

**Full roadmap**: [LEARNING_ROADMAP.md](LEARNING_ROADMAP.md)

---

## 📚 What You'll Learn

### Tutorial 01: Simple Agent ⭐ START HERE
**Time**: 30-45 minutes
**Location**: `tutorials/01-basics/`

**You'll learn**:
- What an AI agent is
- How to call OpenAI API
- System prompts (agent personality)
- Temperature settings
- Building conversations

**Start with**:
1. Read: `tutorials/01-basics/LEARNING_GUIDE.md`
2. Run: `python simple_agent.py`
3. Practice: `python exercises.py`

### Tutorial 02: Memory
**Time**: 45 minutes
**Location**: `tutorials/02-memory/`

**You'll learn**:
- Why agents need memory
- Conversation history
- Different memory types
- Saving/loading conversations

**Start with**:
1. Read: `tutorials/02-memory/MEMORY_EXPLAINED.md`
2. Run: `python agent_with_memory_visualization.py`
3. Test: `python demo_auto.py`

### Tutorial 03A: Tool Integration
**Time**: 45 minutes
**Location**: `tutorials/03-tools/`

**You'll learn**:
- How to structure tool definitions
- When to call tools vs. answer directly
- Handling success and failure paths

**Start with**:
1. Read: `tutorials/03-tools/README.md`
2. Run: `python tool_agent.py`
3. Add your own tool and test it

### Tutorial 03B: MCP Servers
**Time**: 1-2 hours
**Location**: `tutorials/03-mcp-servers/`

**You'll learn**:
- Model Context Protocol (MCP)
- Building MCP servers
- Tools and resources
- Connecting to Claude Desktop

**Start with**:
1. Read: `tutorials/03-mcp-servers/START_HERE.md`
2. Run: `python simple_demo.py`
3. Try: `python interactive_calculator.py`

### Tutorial 04: Planning & Reasoning
**Time**: 60 minutes
**Location**: `tutorials/04-planning/`

**You'll learn**:
- The ReAct reasoning loop
- Task decomposition strategies
- Combining planning with memory and tools

**Start with**:
1. Read: `tutorials/04-planning/README.md`
2. Run: `python planning_agent.py`
3. Inspect the printed reasoning steps

### Tutorial 05: Advanced Patterns
**Time**: 75-90 minutes
**Location**: `tutorials/05-advanced/`

**You'll learn**:
- Retrieval-Augmented Generation (RAG)
- Multi-agent collaboration
- Self-evaluation loops

**Start with**:
1. Read: `tutorials/05-advanced/README.md`
2. Run: `python rag_agent.py`
3. Experiment with `python multi_agent_team.py`

---

## 🎯 Choose Your Path

### Path 1: Guided Learning (Recommended)
Follow the tutorials in order:
1. Tutorial 01 → 02 → 03A → 03B → 04 → 05
2. Read learning guides
3. Complete exercises
4. Build projects

**Best for**: Beginners, systematic learners

### Path 2: Hands-On Learning
Jump straight into coding:
1. Run `tutorials/01-basics/exercises.py`
2. Try modifying examples
3. Refer to guides when stuck
4. Build as you learn

**Best for**: Experienced programmers

### Path 3: Project-Based
Pick a project and learn what you need:
1. Choose from [LEARNING_ROADMAP.md](LEARNING_ROADMAP.md#project-ideas-by-skill-level)
2. Work through relevant tutorials
3. Build while learning
4. Refer to docs as needed

**Best for**: Goal-oriented learners

---

## 📁 Project Structure

```
AI-Agents-from-scratch/
│
├── START_LEARNING_HERE.md       ⭐ YOU ARE HERE
├── LEARNING_ROADMAP.md          Complete learning path
├── README.md                    Project overview
│
├── tutorials/
│   ├── 01-basics/               ⭐ START: Simple agent
│   │   ├── LEARNING_GUIDE.md    Line-by-line explanation
│   │   ├── simple_agent.py      The code to study
│   │   └── exercises.py         Hands-on practice
│   │
│   ├── 02-memory/               Memory & conversations
│   │   ├── agent_with_memory.py
│   │   └── demo_auto.py
│   │
│   ├── 03-tools/                Tool integration patterns
│   │   └── tool_agent.py
│   │
│   ├── 03-mcp-servers/          MCP protocol & tools
│   │   ├── START_HERE.md
│   │   └── simple_demo.py
│   │
│   ├── 04-planning/             ReAct planning & decomposition
│   │   └── planning_agent.py
│   │
│   └── 05-advanced/             RAG, multi-agent, evaluation
│       ├── rag_agent.py
│       └── multi_agent_team.py
│
└── .env                         Your API key (create this!)
```

---

## 🛠️ Prerequisites

### Required
- ✅ Python 3.8 or higher
- ✅ OpenAI API key ([get one here](https://platform.openai.com))
- ✅ Basic Python knowledge (variables, functions, loops)

### Helpful (but not required)
- Understanding of APIs
- Command line basics
- Git basics

---

## 📝 Quick Reference

### Running an Agent
```bash
cd tutorials/01-basics
python simple_agent.py
```

### Checking Setup
```bash
# Is Python installed?
python --version

# Is venv activated? (should see "(venv)" in prompt)
venv\Scripts\activate

# Is OpenAI installed?
python -c "import openai; print('OK')"

# Is API key set?
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OK' if os.getenv('OPENAI_API_KEY') else 'Missing')"
```

### Common Commands
```bash
# Activate venv
venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Run a tutorial
cd tutorials/01-basics
python simple_agent.py

# Run exercises
python exercises.py
```

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'openai'"
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### "OPENAI_API_KEY not found"
1. Create `.env` file in project root
2. Add: `OPENAI_API_KEY=sk-your-key-here`
3. Get key from [platform.openai.com](https://platform.openai.com)

### "Virtual environment not activated"
You should see `(venv)` in your terminal prompt.
```bash
venv\Scripts\activate
```

### "Path with spaces error"
Use quotes:
```bash
cd "c:\Users\Niket Sharma\llmapp\AI-Agents-from-scratch"
```

---

## ✅ Learning Checklist

Before starting:
- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] OpenAI API key obtained
- [ ] `.env` file created with API key
- [ ] Test agent runs successfully

During learning:
- [ ] Completed Tutorial 01
- [ ] Completed Tutorial 02
- [ ] Completed Tutorial 03A (Tools)
- [ ] Completed Tutorial 03B (MCP)
- [ ] Completed Tutorial 04 (Planning)
- [ ] Completed Tutorial 05 (Advanced)
- [ ] Built at least one custom agent
- [ ] Completed hands-on exercises

After tutorials:
- [ ] I understand what an AI agent is
- [ ] I can build agents with different personalities
- [ ] I can implement conversation memory
- [ ] I can integrate tools and build MCP servers
- [ ] I can design planning loops with ReAct
- [ ] I can ground responses with retrieval and multi-agent feedback
- [ ] I've built my own unique agent
- [ ] I'm ready for advanced topics!

---

## 🎓 Learning Tips

### 1. Don't Rush
Take your time with each tutorial. Understanding is more important than speed.

### 2. Type, Don't Copy
Type out the code yourself. You'll learn better!

### 3. Experiment
Change things. Break things. See what happens. That's how you learn!

### 4. Take Notes
Keep a learning journal. Write down key concepts and "aha!" moments.

### 5. Build Projects
After each tutorial, build something with what you learned.

### 6. Ask Questions
If stuck, re-read the guides. They explain everything line-by-line!

---

## 🚀 Your Next Action

**Right now** (5 minutes):
```bash
cd tutorials\01-basics
python simple_agent.py
```

Chat with your first AI agent!

**Then** (30 minutes):

Open in your text editor:
```
tutorials/01-basics/LEARNING_GUIDE.md
```

Read the line-by-line explanation!

**After that** (30 minutes):
```bash
python exercises.py
```

Complete the hands-on exercises!

---

## 📚 Additional Resources

### Documentation
- [LEARNING_ROADMAP.md](LEARNING_ROADMAP.md) - Complete learning path
- [tutorials/01-basics/LEARNING_GUIDE.md](tutorials/01-basics/LEARNING_GUIDE.md) - Line-by-line code explanation
- [tutorials/03-tools/README.md](tutorials/03-tools/README.md) - Tool integration patterns
- [tutorials/03-mcp-servers/README.md](tutorials/03-mcp-servers/README.md) - MCP tutorial
- [tutorials/04-planning/README.md](tutorials/04-planning/README.md) - ReAct planning guide
- [tutorials/05-advanced/README.md](tutorials/05-advanced/README.md) - Advanced retrieval and multi-agent patterns

### Examples
- `tutorials/01-basics/simple_agent.py` - Basic agent
- `tutorials/02-memory/agent_with_memory.py` - Agent with memory
- `tutorials/03-tools/tool_agent.py` - Tool calling
- `tutorials/03-mcp-servers/basic/simple_mcp_server.py` - MCP server
- `tutorials/04-planning/planning_agent.py` - ReAct planner
- `tutorials/05-advanced/rag_agent.py` - Retrieval-augmented agent

### Exercises
- `tutorials/01-basics/exercises.py` - Hands-on practice
- Build your own tool in `tutorials/03-tools/tool_agent.py`
- Capture a planning trace in `tutorials/04-planning/planning_agent.py`

---

## 💡 What You'll Be Able to Build

After completing these tutorials:

**Beginner Level**:
- ✅ Chat bots with different personalities
- ✅ Q&A assistants
- ✅ Language practice bots

**Intermediate Level**:
- ✅ Agents that remember conversations
- ✅ Note-taking assistants
- ✅ Code helpers

**Advanced Level**:
- ✅ Personal assistants with tool access
- ✅ Research assistants
- ✅ Code review agents
- ✅ Retrieval-augmented knowledge bases
- ✅ Multi-agent teams with review loops
- ✅ Your own custom AI agent!

---

## 🎉 Let's Begin!

You're ready to start your AI agent journey!

**Your first step**:

```bash
cd tutorials\01-basics
python simple_agent.py
```

Then open:
```
tutorials/01-basics/LEARNING_GUIDE.md
```

**Happy learning! 🚀**

---

**Questions?** Check [LEARNING_ROADMAP.md](LEARNING_ROADMAP.md) for detailed setup and troubleshooting.

**Stuck?** Re-read the LEARNING_GUIDE.md - it explains every line of code!

**Ready for more?** After Tutorial 01, move to Tutorial 02 (Memory)!
