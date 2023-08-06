from setuptools import setup, find_packages

setup(
    name='wallclock',
    version='1.0',
    author='Owen Jacobson',
    author_email='owen.jacobson@grimoire.ca',
    url='http://bitbucket.org/ojacobson/wallclock',
    
    description='A simple stack-based performance logger',
    
    license='MIT License',
    
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Debuggers',
        'Topic :: System :: Logging',
    ],
    
    py_modules=['wallclock'],
    
    setup_requires=[
        'setuptools_hg'
    ],
    install_requires=[
        'decorator'
    ],
)
