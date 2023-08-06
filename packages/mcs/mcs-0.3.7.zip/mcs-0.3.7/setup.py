from setuptools import setup, find_packages

setup(
    name='mcs',
    version='0.3.7',
    # additional information
    author='Michael Gruenewald',
    author_email='mail@michaelgruenewald.eu',
    description='Monticello repository synchronization tool',
    long_description=open('README').read(),
    license='License :: OSI Approved :: MIT License',
    url='https://bitbucket.org/michaelgruenewald/mcs',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Version Control',
        'Topic :: System :: Archiving :: Mirroring',
    ],
    # technical stuff
    packages=find_packages(),
    requires=['cmdln',
              'httplib2 (>=0.6.0)'],
    entry_points={
        'console_scripts': [
            'mcs = mcs.__main__:main',
        ]
    }
)
