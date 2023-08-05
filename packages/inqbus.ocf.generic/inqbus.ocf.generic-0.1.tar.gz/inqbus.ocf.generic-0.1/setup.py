from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='inqbus.ocf.generic',
      version=version,
      description="Generic OCF resource agents",
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
      keywords='pacemaker OCF resource agent HA',
      author='volker jaenisch',
      author_email='volker.jaenisch@inqbus.de',
      url='http://inqbus.de',
      download_url='http://mypypi.inqbus.de/private/inqbus.ocf.generic',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['inqbus', 'inqbus.ocf'],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
                           extra=[
                                  # 'zope.app.container',
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
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
