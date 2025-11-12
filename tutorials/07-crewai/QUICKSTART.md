# CrewAI Tutorial - Quick Start Guide

Get up and running with CrewAI in 5 minutes!

## Prerequisites

- Python 3.8+
- OpenAI API key (or other LLM provider)
- Virtual environment (recommended)

## Installation

### Step 1: Install Dependencies

From the project root:

```bash
# Install all dependencies including CrewAI
pip install -r requirements.txt
```

Or install CrewAI specifically:

```bash
pip install crewai>=0.11.0 crewai-tools>=0.2.0
```

### Step 2: Set Up Environment Variables

Create or update your `.env` file in the project root:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

### Step 3: Verify Installation

```bash
python -c "import crewai; print(f'CrewAI version: {crewai.__version__}')"
```

## Running the Examples

### Example 1: Simple Introduction (Start Here!)

The easiest way to understand CrewAI basics:

```bash
cd tutorials/07-crewai
python simple_crewai_example.py
```

**What it does**: Creates a 2-agent team (researcher + marketer) for product launch planning.

**Duration**: ~30-60 seconds

### Example 2: Blog Content Team

A realistic 4-agent content creation pipeline:

```bash
python crewai_blog_team.py
```

**What it does**: Research → Write → Edit → Optimize a blog post

**Duration**: ~2-3 minutes

**Try it with**: "The Benefits of AI-Powered Code Assistants"

### Example 3: Advanced Research Team

Complex workflow with custom tools:

```bash
python advanced_crewai_research.py
```

**What it does**: Comprehensive research with documentation, code examples, and fact-checking

**Duration**: ~3-4 minutes

**Try it with**: "Retrieval-Augmented Generation (RAG)"

### Example 4: Comparison Demo

See the difference between CrewAI and custom implementation:

```bash
python comparison_with_custom.py
```

**What it does**: Runs the same task using both approaches and compares them

**Duration**: ~1-2 minutes

## Quick Code Example

Here's the minimal code to create a CrewAI agent team:

```python
from crewai import Agent, Task, Crew, Process

# Create agents
researcher = Agent(
    role='Researcher',
    goal='Find information',
    backstory='Expert researcher',
    verbose=True,
)

# Create tasks
task = Task(
    description='Research AI agents',
    agent=researcher,
    expected_output='Research summary',
)

# Run crew
crew = Crew(
    agents=[researcher],
    tasks=[task],
    process=Process.sequential,
)

result = crew.kickoff()
print(result)
```

## Common Issues & Solutions

### Issue: ModuleNotFoundError: No module named 'crewai'

**Solution**:
```bash
pip install crewai crewai-tools
```

### Issue: OpenAI API Error

**Solution**: Check your `.env` file has the correct API key:
```bash
OPENAI_API_KEY=sk-...
```

### Issue: "Agent not making progress"

**Solution**:
- Make task descriptions more specific
- Check that tools are working
- Increase `max_iter` on the agent

### Issue: Rate limit errors

**Solution**:
- Add delays between API calls
- Use a cheaper model (gpt-3.5-turbo)
- Set `max_iter` lower on agents

## Cost Estimates

Approximate costs using OpenAI GPT-4:

- **Simple example**: $0.01 - $0.03
- **Blog team**: $0.05 - $0.10
- **Research team**: $0.10 - $0.20

Use GPT-3.5-turbo for ~10x cheaper costs:

```python
from langchain.chat_models import ChatOpenAI

cheap_llm = ChatOpenAI(model="gpt-3.5-turbo")

agent = Agent(
    role='Worker',
    llm=cheap_llm,
    ...
)
```

## Next Steps

1. ✅ Run `simple_crewai_example.py` to understand basics
2. ✅ Read [README.md](README.md) for detailed concepts
3. ✅ Run `comparison_with_custom.py` to see framework benefits
4. ✅ Modify examples to experiment
5. ✅ Build your own crew for your use case

## Learning Path

```
simple_crewai_example.py (20 min)
         ↓
   Read README.md (30 min)
         ↓
crewai_blog_team.py (30 min)
         ↓
advanced_crewai_research.py (45 min)
         ↓
comparison_with_custom.py (20 min)
         ↓
Build your own crew! (1-2 hours)
```

## Resources

- **Official Docs**: https://docs.crewai.com/
- **GitHub**: https://github.com/joaomdmoura/crewai
- **Discord**: CrewAI community
- **YouTube**: Search "CrewAI tutorial"

## Getting Help

1. Check the [README.md](README.md) for detailed explanations
2. Review error messages carefully
3. Try the comparison example to understand differences
4. Check official CrewAI docs
5. Open an issue in the main repository

---

**Ready to build?** Start with `simple_crewai_example.py` and have fun creating AI agent teams!
