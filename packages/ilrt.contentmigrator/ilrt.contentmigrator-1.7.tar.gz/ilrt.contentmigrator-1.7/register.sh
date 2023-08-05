rm -fr build dist
svn up
python2.6 setup.py register sdist bdist_egg upload 
