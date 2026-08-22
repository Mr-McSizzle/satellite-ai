from setuptools import setup, find_packages

setup(
    name="satellite-ai",
    version="0.1.0",
    package_dir={
        "controller": "controller/controller",
        "mocks": "controller/mocks",
    },
    packages=["controller", "mocks"],
)
