"""
Advanced CrewAI Example: Research Team with Custom Tools

This tutorial demonstrates advanced CrewAI features:
- Custom tool creation with @tool decorator
- Tool integration with agents
- Hierarchical process (manager delegation)
- Memory and context sharing between agents
- Error handling and validation

Use Case: AI Research Team that investigates technical topics
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
import json
from typing import List, Dict, Any

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()


# ============================================================================
# Custom Tools
# ============================================================================

@tool("Technical Documentation Fetcher")
def fetch_documentation(topic: str) -> str:
    """
    Simulates fetching technical documentation for a given topic.
    In production, this would connect to real documentation APIs.

    Args:
        topic: The technical topic to fetch documentation for

    Returns:
        Formatted documentation content
    """
    # Mock documentation - in production, use real APIs
    docs_database = {
        "transformer": """
        Transformer Architecture Documentation:
        - Introduced in "Attention is All You Need" (2017)
        - Key components: Self-attention mechanism, positional encoding
        - Used in: BERT, GPT, T5, and most modern LLMs
        - Advantages: Parallelizable, handles long-range dependencies
        - Applications: NLP, computer vision, protein folding
        """,
        "rag": """
        Retrieval-Augmented Generation (RAG) Documentation:
        - Combines retrieval and generation for improved accuracy
        - Process: Query -> Retrieve relevant docs -> Generate response
        - Key components: Vector database, embedding model, LLM
        - Benefits: Reduces hallucination, grounds responses in facts
        - Common tools: LangChain, LlamaIndex, ChromaDB
        """,
        "agent": """
        AI Agent Architecture Documentation:
        - Components: LLM, tools, memory, planning system
        - Patterns: ReAct, Plan-and-Execute, AutoGPT
        - Key capabilities: Tool use, multi-step reasoning, memory
        - Frameworks: LangGraph, CrewAI, AutoGen
        - Challenges: Reliability, hallucination, cost optimization
        """,
    }

    # Find relevant documentation
    for key, content in docs_database.items():
        if key in topic.lower():
            return content

    return f"Documentation for '{topic}' not found in database. This is a mock tool - integrate real documentation APIs for production use."


@tool("Code Example Generator")
def generate_code_example(concept: str, language: str = "python") -> str:
    """
    Generates code examples for technical concepts.

    Args:
        concept: The technical concept to demonstrate
        language: Programming language (default: python)

    Returns:
        Code example as a string
    """
    examples = {
        "transformer": '''
# Simple Transformer Attention Mechanism (PyTorch)
import torch
import torch.nn as nn

class SelfAttention(nn.Module):
    def __init__(self, embed_dim, num_heads):
        super().__init__()
        self.multihead_attn = nn.MultiheadAttention(embed_dim, num_heads)

    def forward(self, x):
        # x shape: (seq_len, batch_size, embed_dim)
        attn_output, attn_weights = self.multihead_attn(x, x, x)
        return attn_output

# Usage
model = SelfAttention(embed_dim=512, num_heads=8)
''',
        "rag": '''
# Simple RAG Implementation
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

# Create vector store from documents
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents, embeddings)

# Create RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

# Query
result = qa_chain.run("What is the answer to my question?")
''',
        "agent": '''
# Simple AI Agent with Tools
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.llms import OpenAI

# Define tools
tools = [
    Tool(
        name="Calculator",
        func=lambda x: eval(x),
        description="Useful for math calculations"
    )
]

# Create agent
agent = create_react_agent(
    llm=OpenAI(),
    tools=tools,
    prompt=agent_prompt
)

# Run agent
agent_executor = AgentExecutor(agent=agent, tools=tools)
result = agent_executor.invoke({"input": "What is 15 * 23?"})
''',
    }

    for key, code in examples.items():
        if key in concept.lower():
            return code

    return f"# Code example for '{concept}' in {language}\n# No example available in mock database"


@tool("Research Paper Finder")
def find_research_papers(topic: str, max_results: int = 3) -> str:
    """
    Simulates searching for academic papers on a topic.
    In production, integrate with arXiv, Semantic Scholar, or Google Scholar APIs.

    Args:
        topic: Research topic
        max_results: Maximum number of papers to return

    Returns:
        List of relevant papers with citations
    """
    # Mock research papers
    papers = [
        {
            "title": f"Advances in {topic}: A Comprehensive Survey",
            "authors": "Smith, J., et al.",
            "year": 2024,
            "abstract": f"This paper surveys recent developments in {topic}, highlighting key innovations and future directions.",
            "citations": 156,
            "url": "https://arxiv.org/example/1"
        },
        {
            "title": f"Practical Applications of {topic} in Industry",
            "authors": "Johnson, A., Lee, K.",
            "year": 2023,
            "abstract": f"We demonstrate real-world applications of {topic} across various industries.",
            "citations": 89,
            "url": "https://arxiv.org/example/2"
        },
        {
            "title": f"Theoretical Foundations of {topic}",
            "authors": "Williams, R., et al.",
            "year": 2023,
            "abstract": f"A deep dive into the mathematical and theoretical aspects of {topic}.",
            "citations": 203,
            "url": "https://arxiv.org/example/3"
        },
    ]

    result = f"Research Papers on '{topic}':\n\n"
    for i, paper in enumerate(papers[:max_results], 1):
        result += f"{i}. {paper['title']}\n"
        result += f"   Authors: {paper['authors']} ({paper['year']})\n"
        result += f"   Citations: {paper['citations']}\n"
        result += f"   Abstract: {paper['abstract']}\n"
        result += f"   URL: {paper['url']}\n\n"

    result += "Note: Mock data. Integrate real APIs (arXiv, Semantic Scholar) for production."
    return result


@tool("Fact Checker")
def fact_checker(claim: str) -> str:
    """
    Validates factual claims (mock implementation).

    Args:
        claim: The claim to verify

    Returns:
        Verification result
    """
    # Simple mock validation
    confidence = "Medium"
    status = "Plausible"

    return f"""
    Fact Check Result:
    Claim: {claim}
    Status: {status}
    Confidence: {confidence}
    Timestamp: {datetime.datetime.now().isoformat()}

    Note: This is a mock fact checker. For production, integrate real
    fact-checking APIs and knowledge bases.
    """


# ============================================================================
# Create Specialized Agents
# ============================================================================

def create_research_manager() -> Agent:
    """Creates a manager agent that coordinates the research team."""
    return Agent(
        role='Research Team Manager',
        goal='Coordinate research efforts and ensure comprehensive analysis',
        backstory="""You are an experienced research team lead who excels at
        breaking down complex research questions into manageable tasks and
        coordinating specialists to produce high-quality research outputs.
        You delegate tasks effectively and synthesize results.""",
        verbose=True,
        allow_delegation=True,  # Can delegate to other agents
    )


def create_technical_researcher() -> Agent:
    """Creates a technical research specialist."""
    return Agent(
        role='Technical Research Specialist',
        goal='Gather and analyze technical documentation and research papers',
        backstory="""You are a technical researcher who specializes in finding
        and analyzing academic papers, documentation, and technical resources.
        You're skilled at understanding complex technical concepts and
        summarizing them clearly.""",
        tools=[fetch_documentation, find_research_papers],
        verbose=True,
        allow_delegation=False,
    )


def create_code_analyst() -> Agent:
    """Creates a code analysis specialist."""
    return Agent(
        role='Code Analysis Specialist',
        goal='Provide practical code examples and implementation insights',
        backstory="""You are a senior software engineer who excels at creating
        clear, practical code examples that demonstrate technical concepts.
        You understand best practices and can explain complex implementations
        in accessible ways.""",
        tools=[generate_code_example],
        verbose=True,
        allow_delegation=False,
    )


def create_fact_checker_agent() -> Agent:
    """Creates a fact-checking specialist."""
    return Agent(
        role='Fact Checker',
        goal='Verify claims and ensure accuracy of research findings',
        backstory="""You are a meticulous fact-checker who validates claims,
        cross-references sources, and ensures the accuracy of all information.
        You're skeptical but fair, and you always cite your sources.""",
        tools=[fact_checker],
        verbose=True,
        allow_delegation=False,
    )


# ============================================================================
# Research Team Crew
# ============================================================================

class ResearchTeam:
    """
    Advanced CrewAI research team with hierarchical structure.
    """

    def __init__(self, research_topic: str):
        """
        Initialize the research team.

        Args:
            research_topic: The topic to research
        """
        self.topic = research_topic

        # Create agents
        self.manager = create_research_manager()
        self.tech_researcher = create_technical_researcher()
        self.code_analyst = create_code_analyst()
        self.fact_checker = create_fact_checker_agent()

        # Create tasks
        self.tasks = self._create_tasks()

        # Create crew with hierarchical process
        self.crew = Crew(
            agents=[
                self.manager,
                self.tech_researcher,
                self.code_analyst,
                self.fact_checker
            ],
            tasks=self.tasks,
            process=Process.sequential,  # Use sequential for predictable flow
            verbose=True,
        )

    def _create_tasks(self) -> List[Task]:
        """Create research tasks."""
        tasks = []

        # Task 1: Literature Review
        tasks.append(Task(
            description=f"""
            Conduct a comprehensive literature review on: {self.topic}

            Requirements:
            1. Find and summarize relevant research papers
            2. Gather technical documentation
            3. Identify key concepts and definitions
            4. Note important citations and references

            Use the research paper finder and documentation tools.
            """,
            agent=self.tech_researcher,
            expected_output="Comprehensive literature review with paper summaries and key findings."
        ))

        # Task 2: Code Examples
        tasks.append(Task(
            description=f"""
            Create practical code examples demonstrating: {self.topic}

            Requirements:
            1. Provide clear, well-commented code examples
            2. Show practical implementations
            3. Include usage examples
            4. Explain key implementation details

            Use the code example generator tool.
            """,
            agent=self.code_analyst,
            expected_output="Working code examples with clear explanations and usage instructions."
        ))

        # Task 3: Fact Checking
        tasks.append(Task(
            description=f"""
            Verify the accuracy of claims made about: {self.topic}

            Review the research and code examples for:
            1. Factual accuracy
            2. Consistency with documentation
            3. Validity of technical claims
            4. Proper attribution of sources

            Use the fact checker tool for validation.
            """,
            agent=self.fact_checker,
            expected_output="Fact-check report validating key claims and identifying any concerns."
        ))

        # Task 4: Final Synthesis
        tasks.append(Task(
            description=f"""
            Synthesize all research into a comprehensive report on: {self.topic}

            Combine:
            1. Literature review findings
            2. Code examples and implementations
            3. Fact-check validation results

            Create a well-structured final report that includes:
            - Executive summary
            - Key findings
            - Technical details
            - Code examples
            - References and citations
            - Recommendations for further study
            """,
            agent=self.manager,
            expected_output="Comprehensive research report with all findings synthesized and properly structured."
        ))

        return tasks

    def run(self) -> str:
        """
        Execute the research workflow.

        Returns:
            Final research report
        """
        print(f"\n{'='*80}")
        print(f"Starting Research Team for Topic: '{self.topic}'")
        print(f"{'='*80}\n")

        result = self.crew.kickoff()

        print(f"\n{'='*80}")
        print("Research Complete!")
        print(f"{'='*80}\n")

        return result


# ============================================================================
# Main Function
# ============================================================================

def main():
    """
    Demonstrate advanced CrewAI research team.
    """
    print("\n" + "="*80)
    print("Advanced CrewAI: AI Research Team")
    print("="*80)
    print("\nThis demo showcases:")
    print("  1. Custom tool creation with @tool decorator")
    print("  2. Multiple specialized agents with different tools")
    print("  3. Complex multi-step research workflow")
    print("  4. Coordination and synthesis of results")
    print("\n" + "="*80 + "\n")

    # Get research topic
    topic = input("Enter a research topic (or press Enter for default): ").strip()

    if not topic:
        topic = "Retrieval-Augmented Generation (RAG)"
        print(f"Using default topic: {topic}\n")

    # Create and run research team
    research_team = ResearchTeam(topic)
    final_report = research_team.run()

    # Display results
    print("\n" + "="*80)
    print("FINAL RESEARCH REPORT")
    print("="*80 + "\n")
    print(final_report)

    # Save report
    output_file = Path(f"research_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    output_file.write_text(str(final_report), encoding='utf-8')
    print(f"\n\nReport saved to: {output_file.absolute()}")


if __name__ == "__main__":
    main()
