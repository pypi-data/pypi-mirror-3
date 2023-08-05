from distutils.core import setup


with open('README.rst') as file:
    long_description = file.read()

setup(name="MyPersonalDev",
      version="0.1.2",
      description="open-source personal development software",
      long_description=long_description,
      author="MyPersonalDev Inc.",
      author_email="development@mypersonaldev.com",
      maintainer="Patrick Shields",
      maintainer_email="patrick@mypersonaldev.com",
      url="https://github.com/mypersonaldev/mypersonaldev-python",
      packages=["mypersonaldev"],
      classifiers=["Development Status :: 2 - Pre-Alpha",
                   "Environment :: Web Environment",
                   "Framework :: Django",
                   "Intended Audience :: Developers",
                   "Intended Audience :: Education",
                   "Intended Audience :: End Users/Desktop",
                   "Intended Audience :: Information Technology",
                   "Intended Audience :: Science/Research",
                   "License :: OSI Approved :: Apache Software License",
                   "Natural Language :: English",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.7",
                   "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
                   "Topic :: Scientific/Engineering :: Artificial Intelligence",
                   "Topic :: Scientific/Engineering :: Information Analysis",
                   "Topic :: Scientific/Engineering :: Visualization",
                   "Topic :: Utilities"
                   ]
      )
