from setuptools import setup, find_packages

version = 0.3

setup(
    name = "anybox.recipe.sysdeps",
    version = version,
    author="Christophe Combelles",
    author_email="ccomb@free.fr",
    description="A buildout recipe to check system dependencies",
    license="ZPL",
    long_description=open('README.txt').read() + open('CHANGES.txt').read(),
    url="https://bitbucket.org/anybox/anybox.recipe.sysdeps/overview",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    namespace_packages=['anybox', 'anybox.recipe'],
    install_requires=['setuptools',
                      'zc.buildout'],
    classifiers=[
      'Framework :: Buildout',
      'Intended Audience :: Developers',
      'Topic :: Software Development :: Build Tools',
      'Topic :: Software Development :: Libraries :: Python Modules',
      ],
    entry_points = {'zc.buildout': ['default = anybox.recipe.sysdeps:Dependencies']},
    )


