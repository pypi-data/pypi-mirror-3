from setuptools import setup, find_packages
import os

version = '4.2'

setup(name='quintagroup.plonecaptchas',
      version=version,
      description="quintagroup.plonecaptchas is simple captchas "
                  "implementation for Plone, designed for validating "
                  "human input in insecure forms.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone captcha',
      author='Quintagroup',
      author_email='support@quintagroup.com',
      url='http://svn.quintagroup.com/products/quintagroup.plonecaptchas',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone>=4.0dev',
          'quintagroup.captcha.core>=0.2',
          'quintagroup.formlib.captcha',
          'quintagroup.z3cform.captcha',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
