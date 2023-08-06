from setuptools import setup 

setup(
    name = "cmsplugin-nextlink",
    version = "0.0.2.1",
    description = "This is a link plugin for django-cms 2.2",
    long_description = open("README").read(),
    author = "Jens Kasten",
    author_email = "jens@kasten-edv.de",
    download_url = "http://bitbucket.org/igraltist/cmsplugin-nextlink",
    url = "http://bitbucket.org/igraltist/cmsplugin-nextlink",
    packages = ["cmsplugin_nextlink", "cmsplugin_nextlink.migrations"],
    package_data = {'': ["templates/cmsplugin_nextlink/nextlink_plugin.html"]},
    license = "GPL3",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
   ],
   install_requires = ['distribute', 'django_cms',],
   zip_save = False,
)    
