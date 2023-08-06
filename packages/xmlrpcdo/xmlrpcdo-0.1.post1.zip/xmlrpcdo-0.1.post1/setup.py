from setuptools import setup, find_packages

setup(
    name="xmlrpcdo",
    version="0.1.post1",
    # additional information
    author="Michael Gruenewald",
    author_email="mail@michaelgruenewald.eu",
    description="XML-RPC request fiddler",
    long_description="xmlrpcdo is a simple, self-explaining XML-RPC request fiddler",
    license='License :: OSI Approved :: GPL License',
    url="https://bitbucket.org/michaelgruenewald/xmlrpcdo",
    # technical stuff
    py_modules=['xmlrpcdo'],
    entry_points=dict(
        console_scripts=['xmlrpcdo = xmlrpcdo:main']
    )
)
