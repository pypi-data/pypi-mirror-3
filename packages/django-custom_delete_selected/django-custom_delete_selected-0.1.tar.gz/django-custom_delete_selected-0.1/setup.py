import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='django-custom_delete_selected',
    version='0.1',
    license='ISC',
    description='Customization of delete_selected ModelAdmin action for '
        'post and pre operations.',
    long_description=read('README.rst'),
    url='https://github.com/saippuakauppias/django-custom_delete_selected',
    author='Denis Veselov',
    author_email='progr.mail@gmail.com',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'django'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
