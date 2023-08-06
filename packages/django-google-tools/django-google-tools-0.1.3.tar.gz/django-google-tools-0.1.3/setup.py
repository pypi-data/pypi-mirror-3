from setuptools import setup, find_packages


setup(
    name='django-google-tools',
    version='0.1.3',
    description='A simple Django app for managing Google Analytics and Site Verification codes.',
    author='Orne Brocaar',
    author_email='info@brocaar.com',
    url='http://github.com/LUKKIEN/django-google-tools',
    license='MIT',
    packages=find_packages(),
    include_package_data = True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
