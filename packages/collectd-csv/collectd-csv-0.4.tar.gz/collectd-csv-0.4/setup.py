from distutils.core import setup

setup(
        name='collectd-csv',
        version='0.4',
        author='Ville Petteri Tolonen',
        author_email='petteri.tolonen@gmail.com',
        py_modules=['CollectD_CSV'],
        scripts=['bin/fetchCSV.py','bin/monitorCSV.py'],
        url='http://pypi.python.org/pypi/collectd-csv',
        license='freeBSD',
        description='Fetch CollectD CSV data matching the given parameters.',
        long_description=open('README.txt').read()
     )

