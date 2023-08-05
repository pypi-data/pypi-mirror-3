
from distutils.core import setup

""" django-activity-stream instalation script """
setup(
    name = 'pactivity_stream',
    description = 'generic activity feed system for users',
    author = 'Philipp Wassibauer',
    author_email = 'phil@maptales.com',
    url='http://github.com/philippWassibauer/django-activity-stream',
    download_url='http://github.com/philippWassibauer/django-activity-stream/tarball/master',
    license='MIT',
    version = __import__('activity_stream').__version__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)


