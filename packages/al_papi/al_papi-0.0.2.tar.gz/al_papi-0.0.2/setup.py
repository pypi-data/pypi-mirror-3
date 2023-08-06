import al_papi
from distutils.core import setup
setup(
    name="al_papi",
    version="0.0.2",
    description="AuthorityLabs",
    author="Chavez",
    author_email="support@authoritylabs.com",
    url="http://www.github.com/mtchavez/py_al_papi",
    packages=["al_papi"],
    package_data={},
    install_requires=["simplejson"],
    tests_require=["nose", "pinocchio=0.3"],
    zip_safe=False
)
