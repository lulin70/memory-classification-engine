from setuptools import setup, find_packages

setup(
    name="mce-mcp-server",
    version="1.0.0",
    description="Memory Classification Engine MCP Server for Claude Code, Cursor and other MCP-supported tools",
    author="lulin70",
    author_email="lulin70@example.com",
    packages=find_packages(),
    install_requires=[
        "memory-classification-engine>=0.4.0",
        "PyYAML",
    ],
    entry_points={
        "console_scripts": [
            "mce-mcp-server=mce_mcp_server.server:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)