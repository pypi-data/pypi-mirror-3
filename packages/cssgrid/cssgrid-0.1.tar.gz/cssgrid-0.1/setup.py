try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='cssgrid',
    version='0.1',
    description='Css grid wrapper for use in templating.',
    author='Ian Wilson',
    author_email='ian@laspilitas.com',
    license="BSD",
    url='',
    install_requires=[
        "webhelpers",
    ],
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ]
)
