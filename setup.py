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
    # Latest mysql-connector was weird behavior: https://stackoverflow.com/questions/73244027/character-set-utf8-unsupported-in-python-mysql-connector
    install_requires=['reportlab>=3.6.8', 'Flask>=2.0.0', "mysql-connector-python<=8.0.29", "gunicorn==20.1.0",
                      "pyyaml>=6.0", "qrcode-7.4.2"],
    scripts=['scripts/generate.py'],
    include_package_data=True,
    package_data={
        'wlan-api': ['vpg/templates/*.html', 'vpg/templates/**/*.html']
    },
)
