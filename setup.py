from setuptools import setup

setup(
    name='wlan-api',
    version='0.1',
    packages=['wlan_api'],
    url='',
    license='',
    author='max',
    author_email='',
    description='',
    install_requires=['reportlab>=3.6.8', 'Flask>=2.0.0', "mysql-connector-python>=8.0.28", "gunicorn==20.1.0",
                      "pyyaml>=6.0"],
    scripts=['scripts/generate.py'],
    include_package_data=True,
)
