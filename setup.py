import setuptools
import pathlib

from setuptools import find_packages

here = pathlib.Path(__file__).parent.resolve()

install_requires = (
    (here / "requirements/common.txt").read_text(encoding="utf-8").splitlines()
)


setuptools.setup(
    name="development_environment",
    version="0.0.1",
    author="J. Albert Cruz",
    author_email="jalbertcruz@gmail.com",
    license="MIT",
    package_dir={
        "": "lib",
    },
    packages=find_packages("lib"),
    install_requires=install_requires,
    include_package_data=True,
    scripts=[
        "bin/set-pre-push-hook",
        "bin/set-pre-commit-hook",
    ],
    entry_points={
        "console_scripts": [
            "dot2d2=dev_conversors.main:dot_to_d2",
            "_pre_push=git_policy.pre_push:put_as_pre_push_githook",
            "_pre_commit=git_policy.pre_commit:put_as_pre_commit_githook",
        ],
    },
)
