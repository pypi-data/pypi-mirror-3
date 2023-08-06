#!/usr/bin/env python
from setuptools import setup

setup(
    name = "reviewboard_db_auth",
    description = "Database authentication backend for ReviewBoard",
    version = "201204",

    author = "Shuge Lee",
    author_email = "shuge.lee@gmail.com",
    url = "https://bitbucket.org/shugelee/reviewboard_db_auth",

    packages = ["reviewboard_db_auth"],

   install_requires = [
       "ReviewBoard",
       "Django>=1.3.1",
       "web.py",
   ],

    entry_points = {
        "reviewboard.auth_backends": [
            "rb_db_auth = reviewboard_db_auth:DatabaseAuthBackend",
        ],
    }
)
