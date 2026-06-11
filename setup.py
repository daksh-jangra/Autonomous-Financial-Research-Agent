from setuptools import setup, find_packages

setup(
    name="autonomous_financial_research_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip() for line in open("requirements.txt")
    ],
    python_requires=">=3.10",
)
