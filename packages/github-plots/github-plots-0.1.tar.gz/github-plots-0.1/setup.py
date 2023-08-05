from setuptools import setup


setup(name="github-plots",
      version='0.1',
      description="Alternative plots from GitHub stats.",
      long_description='',
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
      ],
      keywords='git github stats plotting version control',
      author='Scott Torborg',
      author_email='scott@cartlogic.com',
      url='http://github.com/cartlogic/github-plots',
      install_requires=[
          'github2',
      ],
      license='MIT',
      packages=['ghplots'],
      entry_points=dict(console_scripts=['github-plots=ghplots:main']),
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
