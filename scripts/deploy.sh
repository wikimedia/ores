python setup.py sdist bdist_wheel && twine upload dist/* --skip-existing --username $PYPI_USER --password $PYPI_PASS
