from distutils.core import setup

setup(
    name='PyInq',
    version='0.1.0',
    author='Austin Noto-Moniz',
    author_email='metalnut4@netscape.net',
    url='http://pypi.python.org/pypi/pyinq',
    packages=['pyinq','pyinq.asserts','pyinq.tags','pyinq.printers','pyinq.printers.html','pyinq.printers.cli','pyinq.printers.cli.console','pyinq.printers.cli.bash'],
    license='LICENSE',
    description='Python unit test framework, meant as an alternative to unittest.',
    long_description=open('README.txt','r').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Testing'
   ]
)
