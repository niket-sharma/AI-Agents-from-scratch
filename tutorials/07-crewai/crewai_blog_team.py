"""
CrewAI Tutorial: Building a Blog Content Creation Team

This tutorial demonstrates how to use CrewAI to create a multi-agent system
for researching, writing, and editing blog posts. CrewAI simplifies the
orchestration of multiple AI agents working together on complex tasks.

Key Concepts:
- Agents: Individual AI workers with specific roles and expertise
- Tasks: Specific objectives assigned to agents
- Crew: Orchestration layer that coordinates agents and tasks
- Tools: External capabilities agents can use (search, file operations, etc.)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from dotenv import load_dotenv
import requests
from typing import Optional

# Load environment variables
load_dotenv()


# ============================================================================
# Custom Tools
# ============================================================================

@tool("Search Tool")
def search_tool(query: str) -> str:
    """
    Search the web for information. Uses a simple API call.
    In production, you would use Google Search API, SerpAPI, or similar.

    Args:
        query: The search query string

    Returns:
        Search results as a formatted string
    """
    # This is a mock implementation. In production, use real search APIs.
    # Example: SerpAPI, Google Custom Search, or DuckDuckGo API

    # For demonstration, we'll return mock results
    return f"""
    Search Results for: "{query}"

    1. Article: "Understanding {query}"
       Summary: Comprehensive guide covering key aspects of {query}.
       Source: example.com/article1

    2. Research: "Latest trends in {query}"
       Summary: Recent developments and industry insights about {query}.
       Source: research.org/trends

    3. Guide: "{query} Best Practices"
       Summary: Expert recommendations and proven strategies for {query}.
       Source: bestpractices.com/guide

    Note: This is a demonstration. In production, integrate real search APIs.
    """


@tool("Content Quality Checker")
def quality_checker_tool(content: str) -> str:
    """
    Analyzes content quality including readability, structure, and SEO.

    Args:
        content: The content to analyze

    Returns:
        Quality assessment report
    """
    word_count = len(content.split())
    paragraph_count = len([p for p in content.split('\n\n') if p.strip()])

    # Simple readability check (sentences per paragraph)
    sentences = content.count('.') + content.count('!') + content.count('?')
    avg_sentences = sentences / max(paragraph_count, 1)

    readability = "Good" if 3 <= avg_sentences <= 6 else "Needs improvement"

    return f"""
    Content Quality Report:
    ----------------------
    Word Count: {word_count}
    Paragraphs: {paragraph_count}
    Estimated Sentences: {sentences}
    Avg Sentences/Paragraph: {avg_sentences:.1f}
    Readability: {readability}

    Recommendations:
    - {'✓' if word_count >= 500 else '✗'} Sufficient length (500+ words)
    - {'✓' if paragraph_count >= 4 else '✗'} Good structure (4+ paragraphs)
    - {'✓' if readability == "Good" else '✗'} Readable paragraph length
    """


# ============================================================================
# Define Agents
# ============================================================================

def create_researcher_agent() -> Agent:
    """
    Creates a research specialist agent responsible for gathering information.
    """
    return Agent(
        role='Research Specialist',
        goal='Gather comprehensive and accurate information on given topics',
        backstory="""You are an expert researcher with a keen eye for credible sources
        and relevant information. You excel at finding key facts, statistics, and
        insights that form the foundation of great content. You're thorough, accurate,
        and always cite your sources.""",
        tools=[search_tool],
        verbose=True,
        allow_delegation=False,
        max_iter=3,  # Limit iterations to avoid excessive API calls
    )


def create_writer_agent() -> Agent:
    """
    Creates a content writer agent responsible for creating engaging articles.
    """
    return Agent(
        role='Content Writer',
        goal='Create engaging, well-structured, and informative blog posts',
        backstory="""You are a skilled content writer with years of experience in
        creating compelling blog posts. You know how to structure articles for
        maximum readability, use storytelling techniques, and write in a clear,
        engaging style. You excel at transforming research into narratives that
        resonate with readers.""",
        tools=[],
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )


def create_editor_agent() -> Agent:
    """
    Creates an editor agent responsible for reviewing and improving content.
    """
    return Agent(
        role='Senior Editor',
        goal='Review and polish content to meet high editorial standards',
        backstory="""You are a meticulous editor with a sharp eye for detail.
        You ensure content is error-free, well-structured, and aligns with
        best practices. You check for clarity, coherence, grammar, and overall
        quality. You're constructive in your feedback and focused on excellence.""",
        tools=[quality_checker_tool],
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )


def create_seo_specialist_agent() -> Agent:
    """
    Creates an SEO specialist agent to optimize content for search engines.
    """
    return Agent(
        role='SEO Specialist',
        goal='Optimize content for search engines while maintaining quality',
        backstory="""You are an SEO expert who understands how to balance search
        engine optimization with user experience. You know about keyword placement,
        meta descriptions, header structure, and readability. You ensure content
        ranks well without sacrificing quality or readability.""",
        tools=[],
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )


# ============================================================================
# Define Tasks
# ============================================================================

def create_research_task(agent: Agent, topic: str) -> Task:
    """Creates a research task for gathering information on a topic."""
    return Task(
        description=f"""
        Research the topic: "{topic}"

        Your research should cover:
        1. Key concepts and definitions
        2. Current trends and developments
        3. Statistics and data points
        4. Expert opinions and insights
        5. Practical examples or case studies

        Provide a comprehensive research brief that a writer can use to create
        an informative blog post. Include all relevant facts and cite sources.
        """,
        agent=agent,
        expected_output="A detailed research brief with facts, statistics, and insights about the topic."
    )


def create_writing_task(agent: Agent, topic: str) -> Task:
    """Creates a writing task for drafting the blog post."""
    return Task(
        description=f"""
        Using the research provided, write a comprehensive blog post about: "{topic}"

        Requirements:
        1. Write a compelling headline that captures attention
        2. Create an engaging introduction that hooks the reader
        3. Organize content into clear sections with subheadings
        4. Include 5-7 well-developed paragraphs (800-1200 words)
        5. Use examples and concrete details from the research
        6. Write a strong conclusion with key takeaways
        7. Maintain a professional yet conversational tone

        Focus on clarity, flow, and reader engagement.
        """,
        agent=agent,
        expected_output="A complete blog post draft with headline, introduction, body sections, and conclusion."
    )


def create_editing_task(agent: Agent) -> Task:
    """Creates an editing task for reviewing and improving the content."""
    return Task(
        description="""
        Review and edit the blog post draft to ensure high quality.

        Check for:
        1. Grammar, spelling, and punctuation errors
        2. Clarity and coherence of ideas
        3. Logical flow and structure
        4. Paragraph and sentence variety
        5. Tone consistency
        6. Overall readability and engagement

        Use the quality checker tool to assess the content metrics.
        Provide the final polished version of the blog post with any
        necessary improvements.
        """,
        agent=agent,
        expected_output="A polished, error-free final version of the blog post with quality assessment."
    )


def create_seo_optimization_task(agent: Agent, topic: str) -> Task:
    """Creates an SEO optimization task."""
    return Task(
        description=f"""
        Optimize the blog post for SEO without compromising quality.

        Tasks:
        1. Ensure the primary keyword "{topic}" is naturally integrated
        2. Optimize the headline for search engines and click-through rate
        3. Create a compelling meta description (150-160 characters)
        4. Suggest 3-5 relevant keywords to target
        5. Verify header hierarchy (H1, H2, H3) is properly structured
        6. Recommend internal/external linking opportunities
        7. Provide final SEO-optimized version

        Balance SEO best practices with natural, readable content.
        """,
        agent=agent,
        expected_output="SEO-optimized blog post with meta description, keywords, and optimization notes."
    )


# ============================================================================
# Create and Run the Crew
# ============================================================================

class BlogCrewAI:
    """
    Orchestrates a team of AI agents to create high-quality blog content.
    """

    def __init__(self, topic: str):
        """
        Initialize the blog creation crew.

        Args:
            topic: The blog post topic
        """
        self.topic = topic

        # Create agents
        self.researcher = create_researcher_agent()
        self.writer = create_writer_agent()
        self.editor = create_editor_agent()
        self.seo_specialist = create_seo_specialist_agent()

        # Create tasks
        self.research_task = create_research_task(self.researcher, topic)
        self.writing_task = create_writing_task(self.writer, topic)
        self.editing_task = create_editing_task(self.editor)
        self.seo_task = create_seo_optimization_task(self.seo_specialist, topic)

        # Create crew
        self.crew = Crew(
            agents=[self.researcher, self.writer, self.editor, self.seo_specialist],
            tasks=[self.research_task, self.writing_task, self.editing_task, self.seo_task],
            process=Process.sequential,  # Tasks run in sequence
            verbose=True,
        )

    def run(self) -> str:
        """
        Execute the blog creation workflow.

        Returns:
            The final blog post content
        """
        print(f"\n{'='*80}")
        print(f"Starting Blog Creation Crew for: '{self.topic}'")
        print(f"{'='*80}\n")

        result = self.crew.kickoff()

        print(f"\n{'='*80}")
        print("Blog Creation Complete!")
        print(f"{'='*80}\n")

        return result


# ============================================================================
# Main Function
# ============================================================================

def main():
    """
    Main function to demonstrate CrewAI blog creation team.
    """
    print("\n" + "="*80)
    print("CrewAI Blog Content Creation Team")
    print("="*80)
    print("\nThis demo shows how multiple AI agents collaborate to:")
    print("  1. Research a topic")
    print("  2. Write a draft blog post")
    print("  3. Edit and polish the content")
    print("  4. Optimize for SEO")
    print("\n" + "="*80 + "\n")

    # Get topic from user
    topic = input("Enter a blog post topic (or press Enter for default): ").strip()

    if not topic:
        topic = "The Future of AI Agents in Software Development"
        print(f"Using default topic: {topic}\n")

    # Create and run the crew
    crew_ai = BlogCrewAI(topic)
    final_result = crew_ai.run()

    # Display final result
    print("\n" + "="*80)
    print("FINAL BLOG POST")
    print("="*80 + "\n")
    print(final_result)

    # Save to file
    output_file = Path("blog_output.md")
    output_file.write_text(str(final_result), encoding='utf-8')
    print(f"\n\nBlog post saved to: {output_file.absolute()}")


if __name__ == "__main__":
    main()
