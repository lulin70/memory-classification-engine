from setuptools import setup, find_packages

setup(
    name="carrymem",
    version="0.3.0",
    description="CarryMem — 随身记忆库. Let your AI agent remember users. 60%+ zero LLM cost classification + SQLite default storage + Obsidian knowledge base + user declaration + memory profile + namespace isolation.",
    author="lulin70",
    author_email="lulin70@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyYAML",
    ],
    extras_require={
        "api": ["Flask", "aiohttp", "socketio"],
        "llm": ["requests"],
        "testing": ["pytest", "pytest-benchmark", "pytest-asyncio" ],
        "profiling": ["memory-profiler"],
    },
    entry_points={
        "console_scripts": [
            "carrymem=memory_classification_engine.cli:main",
        ],
        "carrymem.adapters": [
            "sqlite=memory_classification_engine.adapters.sqlite_adapter:SQLiteAdapter",
            "obsidian=memory_classification_engine.adapters.obsidian_adapter:ObsidianAdapter",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)