from setuptools import setup, find_packages

VERSION = '0.4'

setup(name="flask-skel",
    version=VERSION,
    description="Basic Flask paster skeleton template",
    long_description=__doc__,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
    ], 
    keywords="wsgi, flask, web development, mongoengine, paster",
    author="Esteban Feldman",
    author_email="esteban.feldman@gmail.com",
    url="http://bitbucket.org/eka/flask-skel/",
    license="BSD",
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "PasteDeploy>=1.3",
        "PasteScript>=1.7",
        "Tempita>=0.4",
    ],
    entry_points="""
    [paste.paster_create_template]
    flask-skel=flaskskel.template:FlaskSkelTemplate
    """,
)
