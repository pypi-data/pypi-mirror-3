from setuptools import setup

import os
execfile(os.path.join("tgwebservices", "release.py"))

setup(
    name="TGWebServices",
    version=version,
    
    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    license=license,
    
    install_requires = [
        "TurboGears >= 1.0",
        "Genshi >= 0.3.4",
        "PEAK-Rules >= 0.5a1.dev-r2555",
    ],
    scripts = [],
    zip_safe=False,
    packages=['tgwebservices', 'tgwebservices.templates'],
    package_data={'tgwebservices': ['templates/*.html']},
    keywords = [
        "turbogears.extension"
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        # if this is an application that you'll distribute through
        # the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Applications',
        
        # if this is a package that includes widgets that you'll distribute
        # through the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Widgets',
    ],
    test_suite = 'nose.collector',
    entry_points="""
    [python.templating.engines]
    wsautoxml = tgwebservices.xml_:AutoXMLTemplate
    wsautojson = tgwebservices.json_:AutoJSONTemplate
    """
    )
    
