from distutils.core import setup
setup(name='pydas',
      version='0.1.5',
      package_dir={'pydas': 'src'},
      packages=['pydas'],
      author='Patrick Reynolds',
      author_email='patrick.reynolds@kitware.com',
      url='http://github.com/midasplatform/pydas',
      install_requres=['requests','simplejson']
      )
