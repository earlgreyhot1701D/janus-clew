"""Setup configuration for Janus Clew."""

from setuptools import setup, find_packages

setup(
    name="janus-clew",
    version="0.2.0",  # Also defined in config.py: APP_VERSION
    description="Evidence-backed coding growth tracking with Amazon Q Developer",
    author="You",
    author_email="you@example.com",
    url="https://github.com/yourusername/janus-clew",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "click>=8.1.7",
        "gitpython>=3.1.40",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "janus-clew=cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)
