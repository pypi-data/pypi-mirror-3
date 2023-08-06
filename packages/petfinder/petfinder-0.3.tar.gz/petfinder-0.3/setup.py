try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

    def find_packages(exclude=None):
        """
        Just stub this. If you're packaging, you need setuptools. If
        you're installing, not so much.
        """
        return

required = [
    'requests',
    'pytz',
    'lxml',
]

scripts = [
]

setup(
    name='petfinder',
    version='0.3',
    description="A simple wrapper around Petfinder's API",
    long_description=open('README.rst').read(),
    author='Greg Taylor',
    author_email='gtaylor@gc-taylor.com',
    url='https://github.com/gtaylor/petfinder-api',
    packages=find_packages(),
    scripts=scripts,
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=required,
    license='BSD',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        ),
    )
