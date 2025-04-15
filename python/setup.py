from setuptools import find_packages, setup

setup(
    name="llamavis",
    version="0.1.0",
    description="Data visualization library for the LlamaSearch.AI ecosystem",
    author="Nik Jois" "Nik Jois" "Nik Jois" "Nik Jois" "Nik Jois",
    author_email="nikjois@llamasearch.ai"
    "nikjois@llamasearch.ai"
    "nikjois@llamasearch.ai"
    "nikjois@llamasearch.ai"
    "nikjois@llamasearch.ai",
    url="https://github.com/llamasearch/llamavis",
    packages=find_packages(),
    package_data={"llamavis": ["static/*.js", "static/*.css"]},
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.2.0",
        "matplotlib>=3.4.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.7",
)
