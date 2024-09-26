from setuptools import setup

setup(
    name='govee_btled_windows',
    version='1.0',

    description='Govee Bluetooth RGB LED Controller - Windows',

    author='Kaleb Byrum',
    author_email='kabyru@outlook.com',

    packages=['govee_btled_windows'],
    install_requires=[
        'bleak',
        'colour'
    ]
)