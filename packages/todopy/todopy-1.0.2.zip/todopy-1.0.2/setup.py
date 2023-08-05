from setuptools import setup, find_packages
import os.path

def readme():
    return open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(
        name = "todopy",
        version = "1.0.2",
        packages = find_packages(),
        install_requires = ['colorama', 'termcolor', 'configparser'],
        tests_require = ['nose', 'lettuce'],
        test_suite = 'tests',
        entry_points = {
            'console_scripts': [
                'todopy = todopy.todopy:main',
                ]
            },

        author = "Ilkka Laukkanen",
        author_email = "ilkka.s.laukkanen@gmail.com",
        description = "Todo.txt in Python",
        long_description = readme(),
        license = "GPLv3",
        keywords = "todo gtd todo.txt",
        url = "https://bitbucket.org/Ilkka/todopy",
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Topic :: Utilities',
            'Environment :: Console',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License (GPL)'
            ]
        )

