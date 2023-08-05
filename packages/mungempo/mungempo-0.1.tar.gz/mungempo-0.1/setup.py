from setuptools import setup, find_packages
setup(name='mungempo',
      version='0.1',
      author='Nick Veitch',
      author_email='nick@evilnick.org',
      url='https://sourceforge.net/projects/mungempo/',
      description='Commandline tool/module for extracting stereo images from.MPO format files',
      py_modules=['mungempo'],
      entry_points = """
        [console_scripts] 
        mungempo = mungempo:main
        """,
      provides=['mungempo'],
      license='GPLv3',
      keywords='3D graphics .MPO stereoscopic anaglyph',
      install_requires = ['PIL>=1.1.6', 'numpy'],
      )