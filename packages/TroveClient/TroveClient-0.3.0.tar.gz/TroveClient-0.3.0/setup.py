from distutils.core import setup

setup(
    name = "TroveClient",
    version = "0.3.0",
    packages = ['troveclient'],
    author = "Nick Vlku",
    author_email = "n@yourtrove.com",
    description = "The YourTrove client lets you access Trove services.  Register your app at http://dev.yourtrove.com",
    url = "http://dev.yourtrove.com",
    license = "MIT",
    long_description="See http://dev.yourtrove.com",
    include_package_data = True,
	install_requires= [
		'python-dateutil',
		'simplejson'
	]
)

