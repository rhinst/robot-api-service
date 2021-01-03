from setuptools import setup
import platform


setup(
  name='robot-api-service',
  version='0.1',
  description='Robot API service',
  url='https://github.com/rhinst/robot-api-service',
  author='Rob Hinst',
  author_email='rob@hinst.net',
  license='MIT',
  packages=['api'],
  data_files=[
    ('config', ['config/default.yaml']),
    ('config/dev', ['config/dev/env.yaml.dist']),
  ],
  install_requires = [
    'redis==3.5.3',
    'himl==0.7.0',
    'flask==1.1.2'
  ],
  test_suite='tests',
  tests_require=['pytest==6.2.1'],
  entry_points={
    'console_scripts': ['api=api.__main__']
  }
)