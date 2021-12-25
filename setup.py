from distutils.core import setup

setup(
  name='ThermiaOnlineAPI',
  packages=['ThermiaOnlineAPI', 'ThermiaOnlineAPI.api', 'ThermiaOnlineAPI.model'],
  version='1.3',
  license='GPL-3.0',
  description='A Python API for Thermia heat pumps using https://online.thermia.se',
  author='Krisjanis Lejejs',
  author_email='krisjanis.lejejs@gmail.com',
  url='https://github.com/klejejs/python-thermia-online-api',
  download_url='https://github.com/klejejs/python-thermia-online-api/releases',
  keywords=['Thermia', 'Online'],
  install_requires=[],
  classifiers=[],
)