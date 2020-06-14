from setuptools import find_packages, setup

__version__ = open("VERSION").read().strip()


setup(
    name="pyrandall",
    version=__version__,  # see file: VERSION
    packages=find_packages(exclude=["tests", "examples"]),
    python_requires=">=3",
    include_package_data=True,
    description="Pyrandall a testsuite framework oriented around data instead of code",
    url="https://github.com/kpn/pyrandall",
    entry_points={"console_scripts": ["pyrandall = pyrandall.cli:main"]},
    install_requires=[
        "jsonschema~=3.2.0",
        "jsondiff~=1.2.0",
        "requests~=2.20",
        "PyYAML~=5.1",
        "Mako~=1.1.3",
        "curlify~=2.2.0",
        "confluent-kafka~=1.0",
        "deepdiff==3.3",
        "pluggy~=0.13.0",
        "Click~=7.0"
    ],
    tests_require=["pytest", "pytest_httpserver", "responses", "vcrpy", "freezegun"],
)
