try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
setup(
    name = "rmtree",
    version = "1.0",
    author = "Jose Luis Naranjo Gomez",
    author_email = "luisnaranjo733@hotmail.com",
    description = ("A sweet and simple python wrapper to shutil.rmtree"),
    #install_requires= ['nose'],
    entry_points = {
    'console_scripts': ['rmtree = rmtree:main']
    },
    #package_data = {'': ['docs/README.txt']},
    #packages=['project folder name'],
    #long_description=read('docs/description.txt')
    py_modules=['rmtree']
)

#MUST THE RUN FROM SAME DIR AS __file__!
