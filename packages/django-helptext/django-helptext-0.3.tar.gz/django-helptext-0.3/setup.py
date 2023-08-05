try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(name='django-helptext',
      version='0.3',
      license="BSD",
      description='A django application for editing django model field help text in the django admin',
      author='Jacob Smullyan',
      author_email='jsmullyan@gmail.com',
      platforms='OS Independent',
      url='http://www.bitbucket.org/smulloni/django-helptext/',
      #download_url='http://www.bitbucket.org/...'
      keywords="django help admin",
      package_dir={'' : '.'},
      packages=("helptext",),
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      )
