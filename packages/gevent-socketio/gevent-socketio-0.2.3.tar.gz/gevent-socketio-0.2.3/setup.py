from setuptools import setup, find_packages

setup(
    name="gevent-socketio",
    version="0.2.3",
    description="SocketIO server based on the Gevent pywsgi server, a Python network library",
    #long_description=open("README.rst").read(),
    author="Jeffrey Gelens",
    author_email="jeffrey@noppo.pro",
    license="BSD",
    url="https://bitbucket.org/Jeffrey/gevent-socketio",
    download_url="https://bitbucket.org/Jeffrey/gevent-socketio",
    install_requires=("gevent-websocket", "anyjson"),
    setup_requires = ("versiontools >= 1.7",),
    packages=find_packages(exclude=["examples","tests"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
)
