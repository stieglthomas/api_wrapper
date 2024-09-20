from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

setup(
    name="api_wrapper",
    version="0.1.0",
    description="Unified API wrappers for Notion, TickTick, Raindrop, Zotero, etc.",
    author="stieglthomas",
    author_email="contact@stieglthomas.de",
    url="https://github.com/stieglthomas/api_wrapper",
    packages=find_packages(),
    install_requires=read_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
