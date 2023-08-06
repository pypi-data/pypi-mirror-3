from setuptools import setup, find_packages

version = '1.0'
tests_require = [
    'plone.testing',
    'plone.app.testing',
    'zope.configuration',
]

setup(
    name='plone.app.imagetile',
    version=version,
    description="Image tile for deco UI",
    long_description=open("README.rst").read(),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
    keywords='plone deco tile',
    author='Thomas Buchberger',
    author_email='t.buchberger@4teamwork.ch',
    url='https://github.com/plone/plone.app.imagetile',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.schema',
        'zope.i18nmessageid',
        'plone.directives.form',
        'plone.tiles',
        'plone.app.tiles',
        ],
    tests_require=tests_require,
    extras_require=dict(test=tests_require),
    entry_points="""
        # -*- Entry points: -*-
        [z3c.autoinclude.plugin]
        target = plone
        """,
    )
