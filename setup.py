from setuptools import setup, find_packages

setup(
    name='vpg',
    version='0.1',
    packages=['vpg'],
    url='',
    license='',
    author='max',
    author_email='',
    description='',
    install_requires=['reportlab==3.5.67', 'Flask==1.1.2', "mysql-connector-python>=8.0.19", "gunicorn==20.0.4"],
    scripts=['vpg/generate.py'],
    include_package_data=True,
)
