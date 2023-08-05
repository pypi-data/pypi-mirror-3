from setuptools import setup, find_packages

version = '1.1.2'

setup(
    name='plone.recipe.haproxy',
    version=version,
    description="Buildout recipe to install haproxy",
    long_description=(
        open('README.txt').read() + '\n' +
        open('CONTRIBUTORS.txt').read() + '\n' +
        open('CHANGES.txt').read()),
    classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
    ],
    keywords='buildout haproxy proxy loadbalancer',
    author='Helge Tesdal',
    author_email='tesdal@jarn.com',
    url='http://pypi.python.org/pypi/plone.recipe.haproxy',
    license='ZPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone', 'plone.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.buildout'
    ],
    entry_points={
        "zc.buildout": ["default = plone.recipe.haproxy:Recipe"],
    },
    )
