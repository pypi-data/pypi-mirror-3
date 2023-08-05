from setuptools import setup, find_packages

setup(
    name='django-whatever',
    version='0.1.0',
    description='Unobtrusive test models creation for django.',
    author='Ilya Baryshev',
    author_email='baryshev@gmail.com',
    url='http://github.com/coagulant/django-whatever',
    packages=['django_any', 'django_any.contrib', 'django_any.tests'],
    include_package_data=True,
    zip_safe=False,
    license='MIT License',
    platforms = ['any'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)

