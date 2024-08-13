from setuptools import setup, find_packages

setup(
    name='TableScraper',  # Replace with your desired package name
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'requests',
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            'extract-tables=webscraping:extract_tables_from_url',  
        ],
    },
    description='A tool for extracting and saving HTML tables as CSV files.',
    author='Amr Elwany',
    author_email='samyamr819"gmail.com',
    url='https://github.com/Amr-sami/TableScraper',  
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
