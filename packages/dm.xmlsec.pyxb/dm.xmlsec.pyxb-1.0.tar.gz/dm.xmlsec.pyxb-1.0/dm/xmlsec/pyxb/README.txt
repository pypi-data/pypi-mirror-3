This package is a tiny wrapper around the ``wssplat`` bundle of ``pyxb``
for XML digital signatures and XML encryption.
It also provides some utilities for initialization and cleanup of
``libxml2` and ``pyxmlsec`` used by ``dm.saml2`` to implement digital signatures.

The package has been tested with ``pyxb`` version 1.1.3.
It may not work with other ``pyxb`` versions.

The package primarily exists to support ``dm.saml2``.
Its importance for other projects is likely small;
direct use of the ``wssplat`` bundle of ``pyxb`` is likely preferable.

``pyxb`` does not yet support ``easy_install``. Therefore, this
package does not declare its dependence on ``pyxb``.
