from setuptools import setup, find_packages


setup(
    name="majira",
    version="0.1",
    description="Jira helper tool",
    author="Daniel Kertesz",
    author_email="daniel@spatof.org",
    url="https://github.com/piger/majira",
    install_requires=[
        'click==6.7',
        'jira==1.0.9',
        'pendulum==1.0.1',
    ],
    include_package_data=True,
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    majira = majira.main:main
    """
)    
