from setuptools import setup, find_packages

setup(
    name="LaserDeMag",
    version="0.1.0",
    author="Gurazda Marek",
    author_email="twoj@email.com",
    description="Demagnetization simulator based on the three temperatures model (3TM)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy>=1.21",
        "scipy>=1.7",
        "matplotlib>=3.4",
        "PyQt6>=6.6",
        "pdoc3>=0.10"
    ],
    entry_points={
        "gui_scripts": [
            "three_tm_gui = three_tm.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
