This package defines the parameterless function ``add_abort_hooks``
which patches `transaction` to support (before and after) abort hooks.

The support is analogous to that of before commit hooks.
Especially, ``transaction._transaction.Transaction`` gets two new methods
``addBeforeAbortHook`` and ``addAfterAbortHook``
analoguous to ``addBeforeCommitHook`` with identical
signature. The hooks are called at the begin or end,
respectively, of `Transaction.abort()`.

Note that the abort hooks are not called when the transaction
is internally aborted during a transaction commit. In this case,
the after commit hooks are called (with ``False`` as first parameter).
Therefore, it is likely that you will register a corresponding
pair of abort hook and after commit hook.
In fact, I had expected that the after commit hooks would be called
during ``abort`` as well, but the ZODB developers decided that not calling
them on ``abort`` is a feature, not a bug.
