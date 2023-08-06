from setuptools import setup

setup(name="romexpander",
      version="0.5",
      author="Devon Meunier",
      author_email="devon.meunier@utoronto.ca",
      url="http://www.cdf.utoronto.ca/~g8m/",
      license="MIT",
      scripts=["romexpander.py"],
      description="NES ROM Expansion script compatible with DvD's " \
                  "ROM Expander Pro.",
      long_description=open("README").read(),
      install_requires=[
          "docopt>=0.3.0",
      ],
)
