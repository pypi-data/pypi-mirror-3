from setuptools import setup, find_packages
#from distutils.core import setup
#from setuptools import setup, find_packages
setup(name='cryptic',
      version='0.0.1',
      description ="""Encrypted messaging using GnuPG""",
      author="Sam Liu",
      author_email="sam@ambushnetworks.com",
      url='http://github.com/samliu/cryptic',
      license='MIT',
      packages=find_packages(exclude=['legacy']),
      entry_points="""
          [console_scripts]
          cryptic = cryptic:crypticcli
        """,
      install_requires = ['simplejson'],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: End Users/Desktop',
                   'Operating System :: OS Independent'
                  ]

      )

