from setuptools import setup, find_packages

setup(
    name='voucher-pdf-generator',
    version='0.1',
    packages=find_packages(),
    url='',
    license='',
    author='max',
    author_email='',
    description='',
    install_requires=['reportlab==3.4.0'],
    scripts=['src/main'],
    include_package_data=True,
)