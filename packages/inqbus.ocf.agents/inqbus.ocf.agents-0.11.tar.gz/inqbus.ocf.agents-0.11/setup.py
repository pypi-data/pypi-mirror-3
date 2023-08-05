from setuptools import setup, find_packages
import os

version = '0.11'

setup(name='inqbus.ocf.agents',
      version=version,
      description="OCF resource agents based on inqbus.ocf.generic",
      long_description=open("README.txt").read() + "\n" +
                       open("HISTORY.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
                  ],
      keywords='pacemaker OCF resource agent HA PID',
      author='volker.jaenisch@inqbus.de',
      author_email='volker.jaenisch@inqbus.de',
      url='http://inqbus.de',
      download_url='http://pypi.python.org/pypi/inqbus.ocf.agents',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['inqbus', 'inqbus.ocf'],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
                           extra=[
                                  ],
                           docs=[
                                 'z3c.recipe.sphinxdoc',
                                 'sphinxcontrib-requirements',
                                 ],
                           test=[
                                'nose',
                                'coverage',
                                ]
                           ),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'inqbus.ocf.generic',
          'python-daemon',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      install_agents = inqbus.ocf.agents.install_agents:main
      openvpn = inqbus.ocf.agents.openvpn:main
      pidagent = inqbus.ocf.agents.pidagent:main
      dummy_daemon = inqbus.ocf.agents.test.dummy_daemon:main
      """,
      )
