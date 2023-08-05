from setuptools import setup

setup(
    name="EggsPacker",
    version="0.1",
    description="A very simple egg fetcher",
    long_description=open("README").read(),
    author="Christophe de Vienne",
    author_email="cdevienne@gmail.com",

    license='Beer-ware',

    zip_safe=True,

    packages=['eggspacker'],

    entry_points={
        "console_scripts": [
            "packeggs=eggspacker.command:main"
        ]
    }
)
