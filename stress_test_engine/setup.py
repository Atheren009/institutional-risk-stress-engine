import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="regulatory-stress-test-engine",
    version="1.0.0",
    author="Quantitative Risk Team",
    author_email="quant@risk.com",
    description="A regulatory stress testing engine for capital adequacy analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.8',
    install_requires=[
        'QuantLib-Python>=1.29',
        'pandas>=1.3.0',
        'numpy>=1.21.0',
    ],
)