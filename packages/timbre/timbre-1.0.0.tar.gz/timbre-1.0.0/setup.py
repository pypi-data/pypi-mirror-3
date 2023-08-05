from distutils.core import setup

setup(
    name='timbre',
    version='1.0.0',
    description='Analysis tools for telemetry collar data',
    author='Ilja Heckmann',
    author_email='ilja.heckmann@gmail.com',
    package_dir={'timbre': 'source'},
    packages=['timbre'],
    url='https://bitbucket.org/elpres/timbre',
    platforms = ['Platform Independent'],
    requires = ['numpy', 'matplotlib'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ]
)
