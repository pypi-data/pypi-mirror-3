from setuptools import setup, find_packages

version = '0.2'

setup(name='Merlot',
      version=version,
      description="A web-based project management software",
      long_description=open("README.txt").read(),
      # Get strings from http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Other/Nonlisted Topic',
      ],
      keywords="grok zope project management",
      author="Emanuel Sartor, Silvestre Huens",
      author_email="emanuel@menttes.com, shuens@menttes.com",
      url="http://code.google.com/p/merlot/",
      license="GPL2",
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'grokui.admin',
                        'z3c.testsetup',
                        'grokcore.startup',
                        'plone.i18n',
                        'zope.browserresource',
                        'z3c.relationfieldui',
                        'WebOb',
                        'z3c.objpath',
                        'zope.app.schema',
                        'zope.pluggableauth',
                        'zope.i18n',
                        'fanstatic',
                        'zope.fanstatic',
                        # Add extra requirements here
                        ],
      entry_points={
          'fanstatic.libraries': [
              'merlot = merlot.resource:library',
          ]}
      )
