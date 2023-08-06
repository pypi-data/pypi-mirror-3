from distutils.core import setup

setup(
    name='pyfaceb',
    version='0.1.4',
    author='Kevin Stanton',
    author_email='kevin@sproutsocial.com',
    packages=['pyfaceb', 'pyfaceb.test'],
    url='https://bitbucket.org/sproutsocial/pyfaceb',
    license='LICENSE.txt',
    install_requires = ['requests >= 0.8'],
    description='Full-featured, lightweight Facebook API wrapper for Graph & FQL.',
    long_description=open('README.txt').read(),
)
