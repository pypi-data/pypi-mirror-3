from distutils.core import setup

setup(
    name='vimeo',
    version='0.1.1',
    author='Nirmal Kumar',
    author_email='rkumarnirmal@gmail.com',
    packages=['vimeo'],
    scripts=['vimeo/client.py'],
    url='https://github.com/rkumarnirmal/python-vimeo',
    license='MIT',
    description='Python module for using Vimeo API.',
    install_requires=[
        "requests == 0.13.1",
        "simplejson >= 2.1.6",
	"oauth2 >= 1.5.170",
    ]
)
