from setuptools import setup

setup(
    name='wtforms-recaptcha',
    version=__import__('wtfrecaptcha').__version__,
    url='http://bitbucket.org/excieve/wtforms-recaptcha',
    license='BSD',
    author='Artem Gluvchynsky',
    author_email='excieve@gmail.com',
    description='Custom WTForms field that handles reCaptcha display and validation',
    long_description=open('README.rst').read(),
    platforms='any',
    packages=['wtfrecaptcha'],
    install_requires=['WTForms>=0.6.1'],
    test_suite='nose.collector',
    tests_require=['nose'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
