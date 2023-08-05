from distutils.core import setup

setup(
    name='django-mobi',
    version='0.1',
    description='Django middleware and view decorator to detect phones and small-screen devices',
    maintainer='Ken Cochrane',
    maintainer_email='KenCochrane@gmail.com',
    url='https://bitbucket.org/kencochrane/django-mobi/',
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    packages=['mobi',],
    long_description=open('README').read(),
)

