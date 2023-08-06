from setuptools import setup

setup(
    name='doppler',
    version='0.3',
    url='http://github.com/nickgartmann/doppler/',
    license='BSD',
    author='Nick Gartmann',
    author_email='nick@rokkincat.com',
    description='A raw SQL migration tool'
                'for managing your database without an ORM.',
    py_modules=['doppler'],
    zip_safe=True,
    platforms='any',
    install_requires=[
        'psycopg2>=2.4.5'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    entry_points={
        "console_scripts":set([
            "doppler = doppler:main"
        ])
    }
)
