from setuptools import setup

version = "0.1.7"

setup(
    name="configure",
    version=version,
    description="configuration toolkit based on YAML",
    author="Andrey Popp",
    author_email="8mayday@gmail.com",
    py_modules=["configure"],
    test_suite="tests",
    zip_safe=False)
