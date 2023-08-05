from distutils.core import setup

setup(name='txlearnbot', version='0.02', author='Clovis Fabricio',
    author_email='python.nosklo@0sg.net', 
    url='http://bitbucket.org/nosklo/txlearnbot',
    packages=['txlearnbot'],
    package_data={
        'txlearnbot': ['*.xml'],
    },
    scripts=['bin/learnbotgui.py'],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: X11 Applications :: GTK',
      'Natural Language :: Portuguese (Brazilian)',
      'Intended Audience :: Education',
      'License :: OSI Approved :: MIT License',
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: Microsoft :: Windows',
      'Operating System :: POSIX',
      'Programming Language :: Python',
      'Topic :: Software Development :: Build Tools',
      ]
)

