from distutils.core import setup

version = '%s.%s' % __import__('django_restapi').VERSION[:2]

setup(name='django-rest-coupedout',
		version=version,
		packages=['django_restapi'],
		author='Andrew E Gall',
		author_email='andrew@coupedout.com',
	)
