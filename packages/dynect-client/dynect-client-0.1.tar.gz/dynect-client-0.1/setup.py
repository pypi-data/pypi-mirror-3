from distutils.core import setup

setup(name='dynect-client',
      version='0.1',
      description='Dynect REST API Client for adding/removing domains',
      author='Zach Goldberg',
      author_email='zach@zachgoldberg.com',
      url='https://github.com/ZachGoldberg/Dynect-REST-Python-Client',
      packages=[
        'dynect_client',
        ],
      classifiers=['Topic :: Internet :: Name Service (DNS)',
                   'Development Status :: 3 - Alpha']
     )
