from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

setup(
    name="ai-commit-generator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered Git commit message generator using various LLM providers",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-commit-generator",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/ai-commit-generator/issues",
        "Documentation": "https://github.com/yourusername/ai-commit-generator#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pathspec>=0.9.0",
        "python-dotenv>=0.19.0",
        "click>=8.0.0",  # For CLI interface
    ],
    extras_require={
        "cohere": ["cohere>=4.0.0"],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.3.0"],
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "pre-commit>=2.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-commit-generator=ai_commit_generator.cli:main",
        ],
    },
    include_package_data=True,
    keywords="git commit ai llm automation development tools",
)
