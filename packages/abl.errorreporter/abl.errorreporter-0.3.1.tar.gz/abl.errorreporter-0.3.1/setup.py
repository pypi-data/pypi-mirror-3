try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='abl.errorreporter',
    version='0.3.1',
    author='Diez B. Roggisch',
    author_email='diez.roggisch@ableton.com',
    description='Lightweight exception recorder, cli part of WebError',
    zip_safe = False,
    install_requires=[
        "TurboMail",
        "Genshi",
        ],
    tests_require=[
        "nose",
        ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
    ],

)
