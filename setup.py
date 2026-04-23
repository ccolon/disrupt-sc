from setuptools import setup, find_packages
import os

# Read version from _version.py
# encoding="utf-8" is explicit so setup.py works on systems whose default
# locale is not UTF-8 (e.g. Windows with cp936/GBK).
version_file = os.path.join(os.path.dirname(__file__), 'src', 'disruptsc', '_version.py')
with open(version_file, encoding="utf-8") as f:
    exec(f.read())

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="disruptsc",
    version=__version__,
    description="A spatial agent-based model to simulate the dynamics supply chains subject to disruptions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Celian Colon",
    author_email="celian.colon.2007@polytechnique.org",
    url="https://github.com/ccolon/disruptsc",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    license="CC BY-NC-ND 4.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10,<3.14",
    install_requires=[
        # Core data processing
        "pandas>=1.3.0,<3.0",
        "numpy>=1.20.0,<2.0",
        
        # Geospatial processing
        "geopandas>=0.11.1,<1.0",
        "shapely>=1.8.0,<3.0",
        
        # Network analysis
        "networkx>=2.8.0,<4.0",
        
        # Scientific computing
        "scipy>=1.7.0,<2.0",
        
        # Configuration and utilities
        "PyYAML>=5.3.0,<7.0",
        "tqdm>=4.60.0,<5.0"
    ],
    entry_points={
        "console_scripts": [
            "disruptsc=disruptsc.run:main",
            "validate-inputs=disruptsc.validate_inputs:main",
        ],
    },
)
