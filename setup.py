"""
Setup script for CodeMetrics
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="codemetrics",
    version="1.0.0",
    author="Automated Agile Framework Team",
    author_email="support@automatedagile.dev",
    description="AI-Powered Development Analytics for the Automated Agile Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jita81/CODEMETRICS",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.9.0",
            "flake8>=6.1.0",
            "mypy>=1.6.0",
        ],
        "dashboard": [
            "flask>=3.0.0",
            "gunicorn>=21.2.0",
            "plotly>=5.17.0",
        ],
        "full": [
            "flask>=3.0.0",
            "gunicorn>=21.2.0",
            "plotly>=5.17.0",
            "pandas>=2.1.0",
            "numpy>=1.24.0",
            "redis>=5.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "codemetrics=codemetrics.__main__:cli",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Jita81/CODEMETRICS/issues",
        "Source": "https://github.com/Jita81/CODEMETRICS",
        "Documentation": "https://github.com/Jita81/CODEMETRICS#readme",
        "Standardized Framework": "https://github.com/Jita81/Standardized-Modules-Framework-v1.0.0",
        "CodeReview": "https://github.com/Jita81/CODEREVIEW",
        "CodeCreate": "https://github.com/Jita81/CODECREATE",
    },
)
