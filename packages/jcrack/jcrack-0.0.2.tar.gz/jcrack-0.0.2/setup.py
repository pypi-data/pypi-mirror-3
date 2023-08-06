import os
from setuptools import setup, find_packages

version = '0.0.2'
README = os.path.join(os.path.dirname(__file__), 'README.txt')
long_description = open(README).read() + 'nn'
setup(name='jcrack',
      version=version,
      description=("Jabbercracky: A Hash-Cracking Web Service"),
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        "Operating System :: POSIX",
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Security :: Cryptography",
        "Topic :: Internet :: WWW/HTTP"
        ],
      install_requires=["celery>=2.4.6", "SQLAlchemy>=0.7.5", "configparser>=3.1.0"],
      setup_requires=["celery>=2.4.6", "SQLAlchemy>=0.7.5", "configparser>=3.1.0"],
      keywords='hash crack md5 lm ntlm jabbercracky jcrack',
      author='awgh',
      author_email='awgh@awgh.org',
      url='http://awgh.org',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'' : 'src'},
      package_data={'': ['cgi-bin/*', 'etc/*']},
      data_files=[
                  ('/etc', ['etc/jcrack.conf.dist']),
                  ('/etc/init.d', ['etc/init.d/jcrackd']),
                  ('/var/www/python/cgi-bin', ['cgi-bin/crack.py']),
                  ('/var/www/python/cgi-bin', ['cgi-bin/recent.py']),
                  ('/var/www/js', ['js/jquery-1.7.1.js']),
                  ('/var/www/js', ['js/jquery.form.js']),
                  ]
      )
