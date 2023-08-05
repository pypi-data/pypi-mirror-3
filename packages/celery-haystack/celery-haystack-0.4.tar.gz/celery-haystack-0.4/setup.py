from os import path
import codecs
from setuptools import setup

read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()

setup(
    name='celery-haystack',
    version=":versiontools:celery_haystack:",
    description='An app for integrating Celery with Haystack.',
    long_description=read(path.join(path.dirname(__file__), 'README.rst')),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    url='http://celery-haystack.rtfd.org/',
    packages=['celery_haystack'],
    license='BSD',
    classifiers=[
        "Development Status :: 4 - Beta",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    install_requires=[
        'django-appconf >= 0.4.1',
    ],
    setup_requires=[
        'versiontools >= 1.8',
    ],
)
