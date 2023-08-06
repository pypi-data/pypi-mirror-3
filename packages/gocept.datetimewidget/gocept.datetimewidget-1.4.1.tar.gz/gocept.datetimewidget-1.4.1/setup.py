from setuptools import setup, find_packages
import os

version = '1.4.1'

setup(name='gocept.datetimewidget',
      version=version,
      description="Integration package for using zc.datetimewidget in Zope 2",
      long_description='\n\n'.join((open("CHANGES.txt").read(),
                                  open("README.txt").read())),
      classifiers=[
        "Programming Language :: Python",
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope2'
        ],
      keywords='date datetime widget zope2 zope3 zope.formlib',
      author='Daniel Havlik',
      author_email='dh@gocept.com',
      url='',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gocept'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zc.datetimewidget',
          'zope.app.publisher'
      ],
      extras_require=dict(
          fanstatic=['fanstatic']),
      entry_points = {
          'fanstatic.libraries': [
              'gocept.datetimewidget=gocept.datetimewidget.resource:Library'],
      },
      )
