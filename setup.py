"""
Setup script for AI Agents from Scratch tutorial repository.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="ai-agents-tutorial",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive tutorial for building AI agents from scratch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AI-Agents-from-scratch",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.12.0",
        "anthropic>=0.18.0",
        "python-dotenv>=1.0.0",
        "tiktoken>=0.6.0",
        "pydantic>=2.6.0",
        "requests>=2.31.0",
        "tenacity>=8.2.0",
        "jsonschema>=4.21.0",
        "python-dateutil>=2.8.2",
        "colorlog>=6.8.0",
        "rich>=13.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "black>=24.0.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "ipykernel>=6.29.0",
        ],
        "ui": [
            "gradio>=4.19.0",
            "streamlit>=1.31.0",
        ],
        "advanced": [
            "chromadb>=0.4.22",
            "numpy>=1.24.0",
            "langchain>=0.1.9",
            "langchain-community>=0.0.24",
            "langchain-openai>=0.0.7",
        ],
        "all": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "black>=24.0.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "jupyter>=1.0.0",
            "ipykernel>=6.29.0",
            "gradio>=4.19.0",
            "streamlit>=1.31.0",
            "chromadb>=0.4.22",
            "numpy>=1.24.0",
            "langchain>=0.1.9",
            "langchain-community>=0.0.24",
            "langchain-openai>=0.0.7",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-agent=src.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
