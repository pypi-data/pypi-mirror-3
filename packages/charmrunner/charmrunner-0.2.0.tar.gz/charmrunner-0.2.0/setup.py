from setuptools import setup, find_packages

setup(name='charmrunner',
      version="0.2.0",
      classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent'],
      author='Kapil Thangavelu',
      author_email='kapil.foss@gmail.com',
      description="Tools for automated distributed juju charm testing.",
      long_description=open("charmrunner/readme.rst").read(),
      url='http://launchpad.net/charmrunner',
      license='GPL',
      packages=find_packages(),
      install_requires=["networkx", "requests"],
      setup_requires=["nose", "mongonose"],
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'juju-record = charmrunner.recorder:main',
              'juju-watch = charmrunner.watcher:main',
              'juju-load-plan = charmrunner.loader:main',
              'juju-plan = charmrunner.planner:main',
              'juju-snapshot = charmrunner.snapshot:main',
              'juju-graph-runner = charmrunner.runner:main',
              ]},
      zip_safe=True,
      )
