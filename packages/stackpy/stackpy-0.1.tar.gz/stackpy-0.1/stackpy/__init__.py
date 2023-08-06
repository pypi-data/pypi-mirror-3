## @mainpage
#
# @section intro Introduction
# Stack.PY is a Python wrapper designed to make it easy to retrieve information
# from the Stack Exchange API. Stack.PY was built from the ground up to be fast,
# flexible, capable, and reliable.
#
# @section features Features
# Here is a short list of features that Stack.PY provides:
#
# - **Automatic pagination:** Stack.PY takes care of pagination so you don't
#   have to. The Request class contains everything you need to step through one
#   or many pages of data.
#
# - **Complete documentation:** Stack.PY is completely 100% documented so that
#   you are never left guessing what method to use or what parameter you need.
#   The documentation is generated directly from the code so what you see in the
#   documentation directly corresponds with the current code.

from api import API
from site import Site
from filter import Filter
from url import APIError