from distutils.core import setup

setup(
    name='DidYouMean',
    version='0.1.2',
    author='Virendra Rajput',
    author_email='virendra.rajput567@gmail.com',
    packages=['didYouMean'],
    scripts=['didYouMean/didYouMean.py'],
    url='http://pypi.python.org/pypi/didYouMean/',
    license='LICENSE.txt',
    description="Access Google's 'Did You Mean' feature from your script",
    long_description=open('README.txt').read(),
    install_requires=[
        "BeautifulSoup >= 3.2.1",
    ],
)