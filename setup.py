from setuptools import setup, find_packages

setup(
    name="agentlens",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.111.0",
        "uvicorn[standard]>=0.30.0",
        "click>=8.1.0",
        "pydantic>=2.7.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.13.0",
        "pandas>=2.2.0",
        "matplotlib>=3.9.0",
        "plotly>=5.22.0",
        "python-multipart>=0.0.9",
        "jinja2>=3.1.0",
        "aiofiles>=23.2.0",
        "httpx>=0.27.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "agentlens=src.cli.main:cli",
        ],
    },
    python_requires=">=3.10",
)
