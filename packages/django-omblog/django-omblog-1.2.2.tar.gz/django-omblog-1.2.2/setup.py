import os
from distutils.core import setup
from omblog import VERSION

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='django-omblog',
    version=VERSION,
    license = 'BSD 3 Clause',
    description='A speedy django blog',
    url='https://github.com/obscuremetaphor/django-omblog',
    author='Obscure Metaphor',
    author_email='hello@obscuremetaphor.co.uk',
    package_data = {
        'omblog' : [
            'templates/omblog/*.html',
            'templates/search/indexes/omblog/*.txt',
            'static/omblog/css/*',
            'static/omblog/js/*',
            'static/omblog/img/*',
            'static/omblog/font/*',
        ]
    },
    packages=[
        'omblog',
        'omblog.templatetags',
        'omblog.tests',
        'omblog.migrations',
    ],
    install_requires = ['beautifulsoup4',
                        'django-picklefield',
                        'pygments',
                        'markdown'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',]
        
)
