from setuptools import setup

import os
#execfile(os.path.join("TGInterface", "release.py"))

setup(
    name="TGInterface",
    version='0.2.5a1',
    description='Provides clients access to models and methods defined on a TurboGears server.',
    #long_description="",
    author='Sam Wright',
    url='http://pypi.python.org/pypi/TGInterface',
    license='MIT',
    long_description="""
    With TurboGears Interface, the developer can write client code as if he 
    were writing it on the server with direct access to server-side models 
    and methods.
    
    It uses the most-excellent TGWebServices package to do the heavy lifting.
    Unfortunately, the latest egg doesn't seem to work so you'll need to 
    install TGWebServices with mercurial
    (``hg clone https://code.google.com/p/tgws.tgws-2/``) in the TurboGears 
    virtualenv (ie. server-side).
    
    Thanks to all who contributed to TGWebServices and TurboGears (and all
    packages contained therein).
    
    Thanks also to Frank v. Delft for his brain farts and SGC (http://www.thesgc.org/)
    for their support.

    
    Features
    --------
    Server-side:
    
     * Works seamlessly with TurboGears
     * Gives access to models and methods that you decorate
     * API automatically created and offered for download
     * If you expose a model and don't create a controller, one is created for you
     * Methods defined in Controllers automatically import and export complex types defined in the API
     * (Optional) Methods can change 'self' to be the the 'self' object that initiated the call client-side


    Client-side:
    
     * Automatically provides access to methods and models defined in the API
     * Code looks identical to server-side code (using SQLAlchemy's ORM)
     * Automatically guesses database relationships to keep client-data up-to-date
     * All calls are made asynchronously and the module is multithread-safe
     * Allows the developer to easily define callback functions for data being updated or server-side methods finishing

    To-do
    -----
    Server-side:
    
     * Implement autherisation in ``ServerSide.ExposeTable`` (should be easy enough to integrate TurboGear's autherisation system)

    Client-side:
    
     * Make it easy to gracefully tell the user of network outage / server error (at the moment, the developer can make error handlers for specific things going wrong, but there's probably a better way to let him know of general faults affecting many systems.)
    
    """,

    install_requires = [
        #"TurboGears2 >= 2.0",
        #"Genshi >= 0.3.4",
        #"PEAK-Rules >= 0.5a1.dev-r2555",
    ],
    scripts = [],
    zip_safe=False,
    packages=['TGInterface'],
    namespace_packages=['TGInterface'],
    classifiers = [
        'Development Status :: 3 - Alpha',
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
    #test_suite = 'nose.collector',
    #wsautojson = 'tgwebservices.json_:AutoJSONTemplate'
    )
    
