import al_papi
from distutils.core import setup
setup(
    name="al_papi",
    version="0.0.4",
    description="AuthorityLabs Partner API Wrapper",
    author="Chavez",
    author_email="support@authoritylabs.com",
    url="http://www.github.com/mtchavez/py_al_papi",
    packages=["al_papi"],
    package_data={},
    install_requires=["simplejson==2.4.0"],
    tests_require=["nose==1.1.2", "pinocchio==0.3"],
    zip_safe=False
)
