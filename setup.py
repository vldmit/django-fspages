from distutils.core import setup

setup(name='django-fspages',
      description='Django application for serving templates from the file system',
      author='Vladimir Dmitriev',
      author_email='vldmit@gmail.com',
      version='0.1',
      packages=['fspages', 'fspages.template.loaders'],
      license='BSD',
      )
