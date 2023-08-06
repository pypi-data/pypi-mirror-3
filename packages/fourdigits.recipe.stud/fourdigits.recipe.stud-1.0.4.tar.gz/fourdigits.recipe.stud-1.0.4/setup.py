from setuptools import setup, find_packages

version = '1.0.4'

setup(
    name='fourdigits.recipe.stud',
    version=version,
    description="Buildout recipe to install stud",
    long_description=(
        open('README.txt').read() + '\n' +
        open('CONTRIBUTORS.txt').read() + '\n' +
        open('CHANGES.txt').read()),
    classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
    ],
    keywords='buildout stud ssl proxy',
    author='Franklin Kingma',
    author_email='franklin@fourdigits.nl',
    url='http://pypi.python.org/pypi/fourdigits.recipe.stud',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['fourdigits', 'fourdigits.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.buildout'
    ],
    entry_points={
        "zc.buildout": ["default = fourdigits.recipe.stud:Recipe"],
    },
    )
