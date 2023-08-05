try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("cfma", ["fma/cfma.pyx"])]

setup(
    name='fma',
    version="0.0.15",
    description='Full Mongo Alchemyst',
    author='anvie',
    author_email='r[@]nosql.asia',
	keywords='fma mongo orm',
    url = "http://www.mindtalk.com/u/anvie",
	download_url = "https://github.com/anvie/fullmongoalchemist",
    install_requires=[
        "pymongo>=0.10.1"
    ],
    setup_requires=["PasteScript>=1.6.3", "Cython>=0.15.1"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={'':['*.so']},
    zip_safe=False,
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
