from setuptools import setup, find_packages

setup(
    name='imaris-cooker',
    version='0.1.0',
    description='A tool for converting IMS format images to TIFF format',
    author='Guanhao Sun',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'h5py',
        'numpy',
        'tifffile',
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'imaris-cooker=imaris_cooker.ims_to_tiff:cli_main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Image Processing',
    ],
)