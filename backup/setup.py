from setuptools import setup, find_packages

setup(
    name="memory-classification-engine",
    version="1.0.0",
    description="A memory classification engine for intelligent memory management",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
            "black"
        ]
    }
)
