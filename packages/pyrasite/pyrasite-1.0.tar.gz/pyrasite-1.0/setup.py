from setuptools import setup, find_packages

version = '1.0'

f = open('README.rst')
long_description = f.read()
f.close()

setup(name='pyrasite',
      version=version,
      description="Inject code into a running Python process",
      long_description=long_description,
      keywords='debugging injection runtime',
      author='Luke Macken',
      author_email='lmacken@redhat.com',
      url='http://pyrasite.fedorahosted.org',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
      ],
      tests_require=['nose'],
      test_suite='nose.collector',
      entry_points="""
          [console_scripts]
          pyrasite = pyrasite.main:main
      """,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: System :: Monitoring',
          'Topic :: Software Development :: Debuggers',
      ],
      )
