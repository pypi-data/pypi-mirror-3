#!/usr/bin/env python
from tsunami import run

from appsample.models import metadata
from appsample.web import route
from appsample.services import donothing


run(debug=True,
    database = 'sqlite:///database.sqlite',
    metadata=metadata,
    num_processes=4,
    webapps=[
        dict(port=8000,
             route=route,
             cookie_secret='hghHhd73ud9(#hg9dh@8401hfHDGfl',
             ),
        ],
    services=[donothing],
    )
