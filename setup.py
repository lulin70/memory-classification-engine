from setuptools import setup, find_packages

setup(
    name="carrymem",
    version="0.3.0",
    description="Your portable AI memory layer. Classify, store, and retrieve what matters across models, tools, and devices.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lulin70/memory-classification-engine",
    author="lulin70",
    author_email="lulin70@example.com",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "memory_classification_engine": ["py.typed"],
    },
    install_requires=[
        "PyYAML",
        "pycld2",
        "langdetect",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "build",
            "twine",
        ],
    },
    entry_points={
        "carrymem.adapters": [
            "sqlite=memory_classification_engine.adapters.sqlite_adapter:SQLiteAdapter",
            "obsidian=memory_classification_engine.adapters.obsidian_adapter:ObsidianAdapter",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    keywords="ai memory classification mcp agent persistence portable",
)
