mistygrind
==========

Abstract
--------

a tool for static analysis of Misty skills and offboard Misty REST API clients


Getting started
---------------

Install this Python package::

  pip install mistygrind

Try to get the version from the command-line::

  mistygrind -V

which should cause a string like "0.1.0" to be printed.
Check for dependencies::

  mistygrind --check-deps

which will decide if dependencies are satisfied, and if not, give hints.
Dependencies include:

* `ESLint <https://eslint.org/>`_


Use as a Misty virtual machine
------------------------------

Try ::

  mistygrind --vm

which will start listening on 127.0.0.1 (localhost) at port 8888.


Testing and development
-----------------------

All tests are in the directory ``tests/``.
Recent results on `Travis CI <https://travis-ci.org/>`_ are available at
https://travis-ci.org/rerobots/mistygrind


Participating
-------------

All participation must follow our code of conduct, elaborated in the file
CODE_OF_CONDUCT.md in the same directory as this README.


License
-------

This is free software, released under the Apache License, Version 2.0.
You may obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
