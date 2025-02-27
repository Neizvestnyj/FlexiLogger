from setuptools import setup, find_packages

# Read long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="FlexiLogger",
    version="1.0.2",
    author="Neizvestnyj",
    author_email="pikromat1995@gmail.com",
    description="A customizable logger and traceback handler for Python applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Neizvestnyj/FlexiLogger",
    packages=find_packages(where="src", include=["FlexiLogger"]),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    package_data={
        "": ["README.md"],
    },
)
