import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README")).read()
version = open(os.path.join(here, "VERSION")).readline().rstrip()

setup(name="icyeye",
      version=version,
      description="Inlining of images into CSS files",
      long_description=README,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Internet :: WWW/HTTP",
        ],
      keywords="css images",
      author="Euan Goddard",
      author_email="euan.goddard+icyeye@gmail.com",
      packages=find_packages(),
      py_modules=[],
      zip_safe=False,
      tests_require = [
        "coverage",
        "nose",
        ],
      install_requires=[],
      extras_require = {
        'nose': ["nose >= 0.11"],
        },
      test_suite="nose.collector",
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      icyeye = icyeye.cli:main
      """,
    )