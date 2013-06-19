from distutils.core import setup

setup(name='django-fspages',
      description='Django application for serving page templates from the file system',
      author='Vladimir Dmitriev',
      author_email='vldmit@gmail.com',
      version='0.2',
      packages=['fspages', 'fspages.template', 'fspages.template.loaders'],
      license='BSD',
      long_description=open('README.rst').read(),
      )
