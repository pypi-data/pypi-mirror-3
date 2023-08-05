#!/usr/bin/env python2

from setuptools import setup, find_packages

def main():
    setup(
        name = "specialDNS",
        version = "0.1",
        packages = ['specialDNS'],
        entry_points = """
            [console_scripts]
                specialDNS = specialDNS.serve:main
                specialDNSAddName = specialDNS.add:add
""",
        install_requires = ['Twisted'])

if __name__ == '__main__': main()
