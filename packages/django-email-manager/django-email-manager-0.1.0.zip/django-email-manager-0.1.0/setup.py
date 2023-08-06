#from distutils.core import setup
from setuptools import setup

# http://guide.python-distribute.org/quickstart.html
# python setup.py sdist
# python setup.py register
# python setup.py sdist upload
# pip install django-email-manager
# pip install django-email-manager --upgrade --no-deps
# Manual upload to PypI
# http://pypi.python.org/pypi/django-email-manager
# Go to 'edit' link
# Update version and save
# Go to 'files' link and upload the file


setup(name='django-email-manager',
      url='https://bitbucket.org/paulocheque/django-email-manager',
      author="paulocheque",
      author_email='paulocheque@gmail.com',
      keywords='python django email',
      description='A simple application to store a summary of system e-mails.',
      license='MIT',

      version='0.1.0',
      packages=['email_manager', 'email_manager.tests', 'email_manager.management.commands'],
      package_data={
          'email_manager': [
              'templates/*',
              'templates/email_manager/*',
          ],
      },
)
