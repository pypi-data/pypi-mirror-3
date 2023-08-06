from setuptools import setup


long_description = '\n\n'.join([
    open('README').read(),
    open('WIDGETS').read(),
    open('AUTHORS').read(),
    open('CHANGES').read(),
    ])


setup(name='django-extrawidgets',
      version='1',
      description='A project exploring the client-side of Django website development',
      long_description=long_description,
      author='Russell Keith-Magee',
      author_email='russell@keith-magee.com',
      url='http://www.bitbucket.org/freakboy3742/django-rays/wiki/',
      packages=['django_extrawidgets'],
      classifiers=['Development Status :: 1 - Planning',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      zip_safe=False,
      tests_require=[],
      include_package_data=True #To include static files in app
      )
