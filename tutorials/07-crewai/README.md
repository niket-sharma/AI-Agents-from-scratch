# Tutorial 07: CrewAI - Building Multi-Agent Teams

Learn how to use CrewAI to create collaborative AI agent teams that work together to solve complex tasks.

## Overview

CrewAI is a powerful framework for orchestrating role-playing, autonomous AI agents. It enables agents to work together as a team, each with specific roles, goals, and tools, to accomplish complex tasks that would be difficult for a single agent.

## What You'll Learn

- **CrewAI Fundamentals**: Understand agents, tasks, crews, and processes
- **Agent Creation**: Build specialized agents with distinct roles and capabilities
- **Tool Integration**: Create and use custom tools with the `@tool` decorator
- **Task Orchestration**: Define sequential and hierarchical workflows
- **Multi-Agent Collaboration**: Coordinate multiple agents to solve complex problems

## Key Concepts

### 1. Agents

Agents are autonomous AI entities with specific roles, goals, and backstories. Each agent:
- Has a defined **role** (e.g., "Research Specialist", "Content Writer")
- Works toward a specific **goal**
- Has a **backstory** that shapes its behavior and expertise
- Can use **tools** to extend its capabilities
- Can **delegate** tasks to other agents (if enabled)

### 2. Tasks

Tasks are specific objectives assigned to agents. Each task includes:
- A detailed **description** of what needs to be done
- The **agent** responsible for completing it
- An **expected output** description
- Optional **context** from previous tasks

### 3. Crews

A Crew orchestrates agents and tasks. It defines:
- The **agents** that are part of the team
- The **tasks** to be completed
- The **process** (sequential or hierarchical)
- Execution settings (verbose mode, memory, etc.)

### 4. Processes

CrewAI supports different workflow patterns:
- **Sequential**: Tasks run one after another in order
- **Hierarchical**: A manager agent delegates tasks to workers

### 5. Tools

Tools extend agent capabilities. You can:
- Use built-in tools from `crewai-tools`
- Create custom tools with the `@tool` decorator
- Give agents access to APIs, databases, file systems, etc.

## Examples in This Tutorial

### 1. Simple CrewAI Example (`simple_crewai_example.py`)

**Purpose**: Learn the basics of CrewAI with a minimal example.

**What it does**:
- Creates a 2-agent team (Market Researcher + Marketing Strategist)
- Demonstrates sequential task execution
- Shows how agents build on each other's work

**Best for**: First-time CrewAI users

**Run it**:
```bash
python tutorials/07-crewai/simple_crewai_example.py
```

### 2. Blog Content Creation Team (`crewai_blog_team.py`)

**Purpose**: Build a realistic content creation pipeline with 4 specialized agents.

**What it does**:
- **Research Specialist**: Gathers information on the topic
- **Content Writer**: Creates engaging blog posts
- **Senior Editor**: Reviews and polishes content
- **SEO Specialist**: Optimizes for search engines

**Features**:
- Custom tools for search and quality checking
- Sequential workflow with clear handoffs
- Realistic content creation pipeline

**Best for**: Understanding practical multi-agent workflows

**Run it**:
```bash
python tutorials/07-crewai/crewai_blog_team.py
```

### 3. Advanced Research Team (`advanced_crewai_research.py`)

**Purpose**: Demonstrate advanced CrewAI features and custom tools.

**What it does**:
- Creates a 4-agent research team
- Uses multiple custom tools (@tool decorator)
- Implements a comprehensive research workflow
- Produces structured research reports

**Agents**:
- **Research Manager**: Coordinates the team
- **Technical Researcher**: Gathers papers and documentation
- **Code Analyst**: Provides implementation examples
- **Fact Checker**: Validates claims and accuracy

**Custom Tools**:
- Technical documentation fetcher
- Code example generator
- Research paper finder
- Fact checker

**Best for**: Advanced users building production systems

**Run it**:
```bash
python tutorials/07-crewai/advanced_crewai_research.py
```

## Installation

Install CrewAI and its dependencies:

```bash
# Install from the main requirements file
pip install -r requirements.txt

# Or install CrewAI specifically
pip install crewai>=0.11.0 crewai-tools>=0.2.0
```

## Environment Setup

CrewAI works with OpenAI by default. Set your API key:

```bash
# In your .env file
OPENAI_API_KEY=your-openai-api-key-here
```

You can also use other LLM providers (Anthropic, local models, etc.) by configuring agents with custom LLM instances.

## Quick Start Guide

### Step 1: Import CrewAI

```python
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
```

### Step 2: Create Agents

```python
researcher = Agent(
    role='Research Specialist',
    goal='Gather comprehensive information on topics',
    backstory='You are an expert researcher...',
    verbose=True,
)

writer = Agent(
    role='Content Writer',
    goal='Create engaging content',
    backstory='You are a skilled writer...',
    verbose=True,
)
```

### Step 3: Define Tasks

```python
research_task = Task(
    description='Research the topic of AI agents',
    agent=researcher,
    expected_output='Comprehensive research findings',
)

writing_task = Task(
    description='Write an article based on research',
    agent=writer,
    expected_output='Well-written article',
)
```

### Step 4: Create and Run the Crew

```python
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
    verbose=True,
)

result = crew.kickoff()
print(result)
```

## Creating Custom Tools

Tools extend what agents can do. Here's how to create them:

```python
from crewai.tools import tool

@tool("Calculator Tool")
def calculate(expression: str) -> str:
    """
    Performs mathematical calculations.

    Args:
        expression: Math expression to evaluate

    Returns:
        Calculation result
    """
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# Give tools to agents
agent_with_tools = Agent(
    role='Data Analyst',
    goal='Analyze numerical data',
    tools=[calculate],
    verbose=True,
)
```

## Best Practices

### 1. Clear Role Definition
- Give each agent a specific, focused role
- Avoid overlapping responsibilities
- Use backstories to guide agent behavior

### 2. Detailed Task Descriptions
- Be specific about what you want
- Include expected output format
- Provide context when tasks depend on each other

### 3. Tool Selection
- Only give agents tools they need
- Create custom tools for domain-specific tasks
- Test tools independently before integration

### 4. Process Selection
- Use **Sequential** for predictable, step-by-step workflows
- Use **Hierarchical** when you need dynamic task delegation
- Start simple (sequential) before trying complex patterns

### 5. Error Handling
- Implement try-catch in custom tools
- Provide clear error messages
- Set reasonable `max_iter` limits on agents

### 6. Cost Management
- Monitor API usage with verbose=False in production
- Set `max_iter` to limit agent iterations
- Use caching when possible
- Consider using cheaper models for simple agents

## Comparison: CrewAI vs. Other Frameworks

| Feature | CrewAI | LangGraph | Custom (this repo) |
|---------|--------|-----------|-------------------|
| Learning Curve | Easy | Moderate | Full control |
| Role-based agents | ✅ Built-in | Manual setup | Manual setup |
| Task orchestration | ✅ Built-in | Manual setup | Manual setup |
| Tool integration | ✅ Simple | ✅ Flexible | ✅ Full control |
| Workflow patterns | Sequential, Hierarchical | State graphs | Custom |
| Best for | Quick prototypes | Complex workflows | Learning internals |

## Common Patterns

### Pattern 1: Research → Write → Review

```python
# Create agents
researcher = Agent(role='Researcher', ...)
writer = Agent(role='Writer', ...)
editor = Agent(role='Editor', ...)

# Create sequential tasks
tasks = [
    Task(description='Research topic', agent=researcher),
    Task(description='Write draft', agent=writer),
    Task(description='Edit content', agent=editor),
]

# Run
crew = Crew(agents=[...], tasks=tasks, process=Process.sequential)
```

### Pattern 2: Manager Delegation

```python
manager = Agent(
    role='Project Manager',
    allow_delegation=True,  # Can delegate to others
)

worker1 = Agent(role='Worker 1', allow_delegation=False)
worker2 = Agent(role='Worker 2', allow_delegation=False)

# Manager can assign work dynamically
crew = Crew(
    agents=[manager, worker1, worker2],
    tasks=[main_task],
    process=Process.hierarchical,
    manager_llm=ChatOpenAI(model="gpt-4"),
)
```

### Pattern 3: Specialized Team with Tools

```python
# Each agent has domain-specific tools
data_analyst = Agent(role='Analyst', tools=[calculator, chart_maker])
researcher = Agent(role='Researcher', tools=[web_search, paper_finder])
writer = Agent(role='Writer', tools=[grammar_checker, seo_analyzer])

crew = Crew(agents=[data_analyst, researcher, writer], ...)
```

## Troubleshooting

### Issue: "Agent is not making progress"
- **Solution**: Provide more specific task descriptions
- Check that tools are working correctly
- Increase `max_iter` if needed

### Issue: "Too many API calls / high costs"
- **Solution**: Set `max_iter` lower on agents
- Use verbose=False to reduce intermediate calls
- Consider using cheaper models for simple tasks

### Issue: "Agents not using tools"
- **Solution**: Mention tools in task descriptions
- Ensure tool descriptions are clear
- Verify tools are properly assigned to agents

### Issue: "Tasks not building on previous results"
- **Solution**: Use sequential process
- Reference previous tasks in descriptions
- Check that agents have context from prior tasks

## Advanced Topics

### Custom LLM Configuration

Use different models for different agents:

```python
from langchain.chat_models import ChatOpenAI

fast_llm = ChatOpenAI(model="gpt-3.5-turbo")
smart_llm = ChatOpenAI(model="gpt-4")

simple_agent = Agent(role='Simple Task', llm=fast_llm)
complex_agent = Agent(role='Complex Task', llm=smart_llm)
```

### Memory and Context

Enable memory for agents to remember across conversations:

```python
crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True,  # Enable memory
)
```

### Callbacks and Monitoring

Track agent progress:

```python
def callback(output):
    print(f"Agent output: {output}")

agent = Agent(
    role='Worker',
    callbacks=[callback],
)
```

## Next Steps

1. **Run the examples** in order: simple → blog team → research team
2. **Modify agents**: Change roles, goals, and backstories
3. **Create custom tools**: Build tools for your domain
4. **Build your own crew**: Apply CrewAI to your use case
5. **Explore advanced features**: Memory, callbacks, custom LLMs

## Resources

- **Official Docs**: https://docs.crewai.com/
- **GitHub**: https://github.com/joaomdmoura/crewai
- **Examples**: https://github.com/joaomdmoura/crewai-examples
- **Discord**: Join the CrewAI community

## Exercises

Try these to deepen your understanding:

1. **Modify the blog team**: Add a fact-checker agent
2. **Create a development team**: Product manager, developer, QA tester
3. **Build a customer support crew**: Triage, specialist, escalation agents
4. **Add real tools**: Integrate actual APIs (Google Search, GitHub, etc.)
5. **Implement hierarchical process**: Create a manager that delegates dynamically

## Time Estimate

- **Simple example**: 15-20 minutes
- **Blog creation team**: 30-45 minutes
- **Advanced research team**: 45-60 minutes
- **Building your own crew**: 1-2 hours

---

**Ready to start?** Begin with [`simple_crewai_example.py`](simple_crewai_example.py) and work your way up!
