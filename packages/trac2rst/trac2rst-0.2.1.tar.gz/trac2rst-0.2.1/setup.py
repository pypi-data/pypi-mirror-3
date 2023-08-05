from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'HISTORY.txt')).read()


version = '0.2.1'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
]


setup(name='trac2rst',
    version=version,
    description="Quick an dirty tool to transform text in Trac Wiki formatting to Restructured Text",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
      'Topic :: Documentation',
      'Topic :: Software Development :: Documentation',
      'Framework :: Trac',
      'Topic :: Text Processing',
      'Topic :: Utilities',
    ],
    keywords='restructuredtext,rst,converter',
    author='Yaco Sistemas',
    author_email='pcaro@yaco.es',
    url='https://bitbucket.org/pcaro/trac2rst',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['trac2rst=trac2rst:main']
    }
)
