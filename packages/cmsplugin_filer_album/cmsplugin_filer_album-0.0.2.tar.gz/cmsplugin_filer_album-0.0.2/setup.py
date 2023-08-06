from setuptools import setup, find_packages

setup(
        name = 'cmsplugin_filer_album',
        version = '0.0.2',
        packages = find_packages(),
        install_requires = [
            'django-cms',
            'filer',
            ],
        author = 'Eugene Slizevich',
        author_email = 'eugene@slizevich.net',
        description = 'DjangoCMS filer plugin for show albums with template selection',
        long_description = open('README').read(),
        license = 'GPL',
        keywords = 'django-cms filer plugin album template',
        include_package_data = True,
        url = 'http://bitbucket.org/ffaxl/cmsplugin-imagealbum'
     )
