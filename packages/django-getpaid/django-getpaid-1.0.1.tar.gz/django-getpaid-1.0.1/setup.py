from distutils.core import setup



setup(
    name='django-getpaid',
    description='Multi-broker payment processor for django',
    version='1.0.1',
    packages=['getpaid',],
    url='https://github.com/cypreess/django-getpaid',
    license='MIT',
    author='Krzysztof Dorosz',
    author_email='cypreess@gmail.com',
    install_requires=['django'],
)
