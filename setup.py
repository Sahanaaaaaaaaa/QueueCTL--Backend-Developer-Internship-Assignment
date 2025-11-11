from setuptools import setup, find_packages

setup(
    name="queuectl",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'queuectl=queuectl.cli.commands:main',
        ],
    },
    author="Sahana B",
    description="CLI-based background job queue system",
    python_requires=">=3.9",
)
