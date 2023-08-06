try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


install_requires = ["webhelpers", "mako", "peppercorn"]


setup(
    name='pepperedform',
    version='0.4.6',
    description='Helpers for using peppercorn with formprocess.',
    author='Ian Wilson',
    author_email='ian@laspilitas.com',
    license="BSD",
    url='',
    install_requires=install_requires,
    test_requires=install_requires + ['webob'],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ]
)
