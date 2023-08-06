from setuptools import setup

setup(
    name = 'django-simple-s3storage',
    install_requires = ['boto', 'Django==1.4'],
    version = '0.1',
    py_modules = ['S3Storage'],
    author = 'Bryan McLemore',
    author_email = 'kaelten@gmail.com',
    license = 'BSD',
    description = 'A simple django storage backend for Amazon S3 built ontop of Boto.',
    url='http://www.kaelten.com/django-simple-s3storage',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe = False,
)

