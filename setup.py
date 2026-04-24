from setuptools import setup, find_packages

def get_version():
    try:
        from memory_classification_engine.__version__ import __version__
        return __version__
    except ImportError:
        return "0.4.2"

setup(
    name="carrymem",
    version=get_version(),
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
        "memory_classification_engine": [
            "py.typed",
            "semantic/data/*.yaml",
        ],
    },
    install_requires=[
        "PyYAML>=5.0",
        "pycld2>=0.41",
        "langdetect>=1.0.9",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "build>=0.10",
            "twine>=4.0",
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
