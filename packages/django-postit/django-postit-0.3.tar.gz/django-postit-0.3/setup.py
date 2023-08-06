from setuptools import setup, find_packages

setup(
    name='django-postit',
    version=__import__('postit').__version__,
    license="BSD",

    install_requires = [
        "django"
    ],

    description='django-postit is a scrumboard application for django projects',
    long_description=open('README.rst').read(),

    author='0xPr0xy',
    author_email='0xPr0xy@gmail.com',

    url='http://github.com/0xPr0xy/django-postit',
    download_url='http://github.com/0xPr0xy/django-postit/downloads',

    include_package_data=True,

    packages=['postit', 'postit.colors'],

    zip_safe=False,
    classifiers=[
        #'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
