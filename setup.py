from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcdo",
    version="0.1.0",
    author="Roland Albert Romero",
    author_email="romero.rolandalbert@gmail.com",
    description="Monte Carlo Diffraction Optics - Simulation methods for optical diffraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/romeroraa/mcdo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "jupyter>=1.0.0",
            "notebook>=6.0.0",
        ],
    },
)
