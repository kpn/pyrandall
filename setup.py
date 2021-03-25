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
        "jsonschema",
        "jsondiff",
        "requests~=2.20",
        "PyYAML==5.4",
        "Mako",
        "curlify",
        "confluent-kafka~=1.0",
        "deepdiff==3.3",
        "pluggy",
    ],
    tests_require=["pytest", "pytest_httpserver", "responses", "vcrpy", "freezegun"],
)
