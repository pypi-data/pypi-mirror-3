VERSION = '0.0.8'

from setuptools import setup, find_packages

setup(
      name='podcaster',
      version=VERSION,
      author='Pierre Meyer',
      author_email='meyer.p@gmail.com',
      license='BSD',
      description="Podcaster is a Nagare application used to convert a youtube channel to an itunes podcast.",
      long_description=open('README.txt').read(),
      keywords='Nagare Youtube iTunes podcast RSS',
      url='https://bitbucket.org/droodle/podcaster',
      packages=find_packages(),
      include_package_data=True,
      package_data={'' : ['*.cfg']},
      zip_safe=False,
      install_requires=('nagare', 'restkit', 'requests'),
      message_extractors={ 'podcaster' : [('**.py', 'python', None)] },
      entry_points="""
      [nagare.applications]
      podcaster = podcaster.app:app
      """,
      classifiers=('Development Status :: 4 - Beta',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python')
     )

