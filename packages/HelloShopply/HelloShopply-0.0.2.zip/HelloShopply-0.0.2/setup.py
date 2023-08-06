from distutils.core import setup

setup(
    name='HelloShopply',
    version='0.0.2',
    author='Shopply',
    author_email='contactus@shopply.com',
    packages=['helloshopply.code', 'helloshopply.test'],
    scripts=[],
    url='https://github.com/anandrjoshi/helloshopply/',
    license='LICENSE.txt',
    description='Hello Shopply',
    long_description=open('README.txt').read(),
    install_requires=[
        "pyes >= 0.19.1",
        "tornado >= 2.4",
    ],
)