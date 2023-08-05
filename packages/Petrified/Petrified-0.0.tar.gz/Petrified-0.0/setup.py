from setuptools import setup, find_packages


setup(
    name="Petrified",
    version="0.0",

    author="Derek McTavish Mounce",
    author_email="derek@hazelspace.com",
    description="Scary form toolkit of a solidifying nature.",
    license="MIT",

    packages=find_packages(".", exclude=["test_*"]),
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        "jinja2"
    ]
)
