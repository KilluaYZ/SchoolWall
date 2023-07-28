from setuptools import find_packages, setup
# 1234c
setup(
    name='schoolwall',
    version='1.0.0',
    packages=[
        'schoolwall',
        'schoolwall.auth',
        'schoolwall.database',
        'schoolwall.mainpage',
        'schoolwall.manage',
        'schoolwall.utils',
        'schoolwall.monitor',
        ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'PyMySql',
        'flask_cors',
        'sqlalchemy',
        'DButils',
        'wordcloud',
        'psutil',
        'flask_apscheduler'
    ],
)