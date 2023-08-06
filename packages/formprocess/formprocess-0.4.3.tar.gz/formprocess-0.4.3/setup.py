try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='formprocess',
    version='0.4.3',
    description='Form Process is a simple library for processing html forms.',
    author='Ian Wilson',
    author_email='ian@laspilitas.com',
    license="BSD",
    url='',
    install_requires=[
        "webhelpers",
        "formencode",
        "decorator",
        "webob",
    ],
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ]
)
