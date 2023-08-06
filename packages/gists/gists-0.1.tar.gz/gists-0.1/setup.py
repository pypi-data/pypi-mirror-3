from setuptools import setup

README = open('README').read()

setup(
        name='gists',
        packages=['gists'],
        version='0.1',
        author='Jaume Devesa',
        author_email='jaumedevesa@gmail.com',
        url='http://jdevesa.github.com/gists',
        description='CLI interface for manage Github gists',
        install_requires=['requests', 'clint'],
        scripts=['gists/gists'],
        include_package_data=True,
        long_description=README,
        license='MIT',
        test_suite='tests',
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Development Status :: 5 - Production/Stable ",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: POSIX :: Linux"
            ]
)
