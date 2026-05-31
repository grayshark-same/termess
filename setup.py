from setuptools import setup

setup(
    name="termess",
    py_modules=["client"],
    entry_points={
        "console_scripts": [
            "termess=client:run",
        ],
    },
)
