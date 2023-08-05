# Copyright (C) 2011 by Dr. Dieter Maurer <dieter@handshake.de>
"""(Before) abort hooks for `transaction`."""
from logging import getLogger

from transaction._transaction import Transaction


logger = getLogger(__name__)


def add_abort_hooks():
  if hasattr(Transaction, "addBeforeAbortHook"):
    # looks as if the function is already there, do nothing
    return
  logger.info("patching `transaction._transaction.Transaction` for before abort hooks")
  Transaction.addBeforeAbortHook = _add("before")
  Transaction.addAfterAbortHook = _add("after")
  Transaction._bah_ori_abort = Transaction.abort
  Transaction.abort = abort


#############################################################################
## internal
hook_attr_pattern = "_%s_abort"

def _add(type):
  """return an add abort hook method for *type*."""
  hook_attr = hook_attr_pattern % type
  def addAbortHook(self, hook, args=(), kws=None):
    if kws is None: kws = {}
    hooks = getattr(self, hook_attr, [])
    hooks.append((hook, tuple(args), kws))
    setattr(self, hook_attr, hooks)
  addAbortHook.func_name = "add%sAbortHook" % type.capitalize()
  return addAbortHook

# Note: we change the signature (to cope with signature change between versions)
def abort(self, *args, **kw):
  def run_hooks(type):
    hook_attr = hook_attr_pattern % type
    hooks =  getattr(self, hook_attr, None)
    if hooks is not None:
      # run the hooks
      for hook, hargs, hkw in hooks:
        try:
          hook(*hargs, **hkw)
        except:
          self.log.exception("Error in %s abort hook %s", type, hook)
      delattr(self, hook_attr)
  if len(args) > 0: subtransaction = args[0]
  else: subtransaction = kw.get("subtransaction")
  if not subtransaction: run_hooks("begin")
  r = self._bah_ori_abort(*args, **kw)
  if not subtransaction: run_hooks("after")
  return r


