# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Utilities."""

class InitializationError(Exception):
  """Exception indicating initialization problems.

  Not yet used for (potential) problems with ``libxml2`` initialization.
  """

def default_init():
  """default parser and xmlsec initialization."""
  default_parser_init()
  default_xmlsec_init()


def default_parser_init():
  from libxml2 import initParser, substituteEntitiesDefault

  initParser()
  substituteEntitiesDefault(1)


def default_xmlsec_init():
  from xmlsec import init, checkVersion, cryptoAppInit, cryptoInit

  _call_and_check(0, init)
  _call_and_check(1, checkVersion)
  _call_and_check(0, cryptoAppInit, None)
  _call_and_check(0, cryptoInit)


def default_cleanup():
  """default parser and xmlsec cleanup."""
  default_xmlsec_cleanup()
  default_parser_cleanup()


def default_parser_cleanup():
  from libxml2 import cleanupParser
  cleanupParser()


def default_xmlsec_cleanup():
  from xmlsec import cryptoShutdown, cryptoAppShutdown, shutdown

  cryptoShutdown()
  cryptoAppShutdown()
  shutdown()


def create_default_keys_manager():
  from xmlsec import KeysMngr, cryptoAppDefaultKeysMngrInit
  mngr = KeysMngr()
  if mngr is None: raise InitializationError('creating keys manager failed')
  # Note: we lose memory in case of an exception
  _call_and_check(0, cryptoAppDefaultKeysMngrInit, mngr)
  return mngr
  

def _call_and_check(rv, f, *args):
  xrv = f(*args)
  if xrv != rv:
    raise InitializationError('call %s%s failed: %s', f, args, xrv)
