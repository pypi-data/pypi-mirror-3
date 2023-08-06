from setuptools import setup

setup(name="haste",
      version="0.4",
      author="Devon Meunier",
      author_email="devon.meunier@utoronto.ca",
      url="http://www.cdf.utoronto.ca/~g8m/",
      license="MIT",
      scripts=["haste.py"],
      description="Pure Python replacement of the hastebin.com client.",
      install_requires=[
          "docopt>=0.3.0",
      ],
)
