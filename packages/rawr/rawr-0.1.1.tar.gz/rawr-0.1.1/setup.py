import sys, os
try:
    from setuptools import setup
    kw = {'entry_points':
          """[console_scripts]\nrawr= rawr:main\n""",
          'zip_safe': False}
except ImportError:
    from distutils.core import setup
    kw = {'scripts': ['scripts/rawr']}

here = os.path.dirname(os.path.abspath(__file__))

setup(name='rawr',
      version="0.1.1",
      description="Growl Network Interface",
      long_description="""
A python network interface and command line utility for sending growl
notifications to a OSX host.

Initially I created this to allow me to send growl notifications from virtual
machines running on my MacBook.
      """,
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        ],
      keywords='growl',
      author='Dougal Matthews',
      author_email='dougal85@gmail.com',
      maintainer='Dougal Matthews',
      maintainer_email='dougal85@gmail.com',
      url='https://github.com/d0ugal/rawr',
      license='MIT',
      py_modules=['rawr'],
      packages=['rawr'],
      **kw
      )

