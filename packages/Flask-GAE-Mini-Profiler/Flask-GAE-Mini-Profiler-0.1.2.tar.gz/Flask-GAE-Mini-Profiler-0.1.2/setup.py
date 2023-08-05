"""
Flask-GAE-Mini-Profiler
-----------------------

A drop-in, ubiquitous, production profiling tool for
`Flask <http://flask.pocoo.org>`_ applications on Google App Engine using
`gae_mini_profiler <http://bjk5.com/post/6944602865/google-app-engine-mini-profiler>`_.

Links
`````

* `documentation <http://packages.python.org/Flask-GAE-Mini-Profiler>`_
* `development version
  <http://github.com/passy/flask-gae-mini-profiler/zipball/master#egg=Flask-GAE-Mini-Profiler-dev>`_
"""
from setuptools import setup


def run_tests():
    from tests import suite
    return suite()


setup(
    name='Flask-GAE-Mini-Profiler',
    version='0.1.2',
    url='http://packages.python.org/Flask-GAE-Mini-Profiler',
    license='MIT',
    author='Pascal Hartig',
    author_email='phartig@rdrei.net',
    description='Flask integration of gae_mini_profiler',
    long_description=__doc__,
    packages=['flaskext', 'flaskext.gae_mini_profiler'],
    package_data = {
        'flaskext.gae_mini_profiler': [
            'templates/*',
            'static/js/*',
            'static/css/*',
        ]
    },
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    tests_require=['mock==0.7'],
    test_suite="__main__.run_tests",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
