from setuptools import setup, find_packages

# Read long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="OmniLogger",
    version="1.0.0",
    author="Neizvestnyj",
    author_email="pikromat1995@gmail.com",
    description="A customizable logger and traceback handler for Python applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Neizvestnyj/OmniLogger",
    packages=find_packages(where="src", include=["OmniLogger"]),
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
