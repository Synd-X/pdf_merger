from setuptools import setup, find_packages

setup(
    name='pdf_merger',
    version='0.1',
    description='A tool to merge multiple PDFs with custom order, titles, and bookmarks',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Synd-X',
    author_email='syndxx@proton.me',
    url='https://github.com/synd-x/pdf_merger',  # Optional if you plan to host on GitHub
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'PyPDF2>=3.0.0',  # Add other dependencies if necessary
    ],
    entry_points={
        'console_scripts': [
            'pdf-merger=pdf_merger.pdf_merger:main',  # Creates 'pdf-merger' command
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
