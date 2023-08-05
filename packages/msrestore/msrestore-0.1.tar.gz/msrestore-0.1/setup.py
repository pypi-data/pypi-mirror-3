from setuptools import setup


setup(name="msrestore",
      version='0.1',
      description="Backup sync aid for mysql-zrm and more.",
      long_description='',
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
      ],
      keywords='mysql backup restore copy',
      author='Scott Torborg',
      author_email='scott@cartlogic.com',
      url='http://github.com/cartlogic/msrestore',
      license='MIT',
      packages=['msrestore'],
      entry_points=dict(console_scripts=['msrestore=msrestore:main']),
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
