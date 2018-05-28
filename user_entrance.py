#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SunEye.settings")
    import django

    django.setup()
    from backstage import main

    portal = main.call(sys.argv[1:])
