from setuptools import find_packages, setup

setup(
      name='CodeViking.Collections',
      version='0.10',
      namespace_packages=['codeviking',
                          'codeviking.collections',
                          'codeviking.collections.dict'],
      url='http://hg.codeviking.com/collections/',
      author='Dan Bullok',
      author_email='opensource@codeviking.com',
      description='Data collection objects',
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules'
            ],
      platforms='any',
      packages=find_packages(),
      license="GNU GPLv3",
      )

