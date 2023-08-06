from setuptools import setup, find_packages

version = '1.1'

setup(name='tlspu.cookiepolicy',
      version=version,
      description='A Plone add-on providing simple a simple solution to comply with the so called "European Cookie Law".',
      long_description="""In 2011 the European Parliament passed into European Law the ePrivacy Directive (The so called "European Cookie Law").
One of the effects of this law is that anyone who runs a website which sets cookies (Such as Plone sites may) is breaking the law if they fail to notify (And get permission) for these cookies to be set.
TLSPU Cookie Policy is a simple add on for your plone sites which displays a customisable message which enables you to comply with the "Implied Consent" variant which has been adopted into law in certain EU countries.
For sites outside of the EU, or targetting non-EU users it's a reasonable idea to inform your users of the fact your site sets cookies so this may still be useful to you.""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='python plone zope cookie eu law',
      author='TLSPU',
      author_email='contact@tlspu.com',
      url='http://www.tlspu.com/consultancy/cookiepolicy',
      license='AGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['tlspu'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
		  [z3c.autoinclude.plugin]
	      target = plone
      # -*- Entry points: -*-
      """,
      )
