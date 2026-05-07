from setuptools import setup


setup(
    name="aion-news-to-signal",
    version="1.0.2",
    description="AION India Event Intelligence client library and MCP server for Indian financial news analysis. API key required for inference.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=["aion_news_to_signal"],
    py_modules=["aion"],
    include_package_data=False,
    install_requires=[
        "requests>=2.31",
        "mcp>=1.27",
    ],
    entry_points={
        "console_scripts": [
            "aion-news-to-signal-mcp=aion_news_to_signal.mcp_server:main",
        ]
    },
    python_requires=">=3.10",
)
