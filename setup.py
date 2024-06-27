from setuptools import setup, find_packages

setup(
    name='articles_sync',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    author='CyberTM',
    author_email='zhyj_su@163.com',
    description='本地markdown同步至平台,支持csdn,知乎,掘金,简书',
    long_description=open('README.md',encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/your-repo',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
    install_requires=[
        'click',
        'diskcache',
        'DrissionPage',
        'keyring',
        'Requests',
        'setuptools',
    ],
    entry_points={
        'console_scripts': [
            'articles_sync=articles_sync.scripts.sync:cli',
        ],
    },
)