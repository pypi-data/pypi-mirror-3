"""
Transation support for Gaphor
"""

from logging import getLogger
from zope import interface, component
from gaphor.interfaces import ITransaction
from gaphor.event import TransactionBegin, TransactionCommit, TransactionRollback
from gaphor import application

logger = getLogger('transaction')

def transactional(func):
    """The transactional decorator makes a function transactional.  A
    Transaction instance is created before the decorated function is called.
    If calling the function leads to an exception being raised, the transaction
    is rolled-back.  Otherwise, it is committed."""
    
    def _transactional(*args, **kwargs):
        r = None
        tx = Transaction()
        try:
            r = func(*args, **kwargs)
        except Exception, e:
            log.error('Transaction terminated due to an exception, performing a rollback', exc_info=True)
            try:
                tx.rollback()
            except Exception, e:
                log.error('Rollback failed', exc_info=True)
            raise
        else:
            tx.commit()
        return r
    return _transactional

class TransactionError(Exception):
    """
    Errors related to the transaction module.
    """

class Transaction(object):
    """
    The transaction. On start and end of a transaction an event is emited.

    Transactions can be nested. If the outermost transaction is committed or
    rolled back, an event is emitted.

    Events can be handled programmatically:

    >>> tx = Transaction()
    >>> tx.commit()

    It can be assigned as decorator:

    >>> @transactional
    ... def foo():
    ...     pass

    Or with the ``with`` statement:

    >>> with Transaction():
    ...     pass
    """

    interface.implements(ITransaction)

    component_registry = application.inject('component_registry')

    _stack= []

    def __init__(self):
        """Initialize the transaction.  If this is the first transaction in
        the stack, a TransactionBegin event is emited."""
        
        self._need_rollback = False
        if not self._stack:
            self._handle(TransactionBegin())
        self._stack.append(self)

    def commit(self):
        """Commit the transaction.  First, the transaction is closed.
        If it needs to be rolled-back, a TransactionRollback event is emited.
        Otherwise, a TransactionCommit event is emited."""
        
        self._close()
        if not self._stack:
            if self._need_rollback:
                self._handle(TransactionRollback())
            else:
                self._handle(TransactionCommit())

    def rollback(self):
        """Roll-back the transaction.  First, the transaction is closed.
        Every transaction on the stack is then marked for roll-back.  If
        the stack is empty, a TransactionRollback event is emited."""
        
        self._close()
        for tx in self._stack:
            tx._need_rollback = True
        else:
            if not self._stack:
                self._handle(TransactionRollback())

    def _close(self):
        """Close the transaction.  If the stack is empty, a TransactionError
        is raised.  If the last transaction on the stack isn't this transaction,
        a Transaction error is raised."""
        
        try:
            last = self._stack.pop()
        except IndexError:
            raise TransactionError, 'No Transaction on stack.'
        if last is not self:
            self._stack.append(last)
            raise TransactionError, 'Transaction on stack is not the transaction being closed.'

    def _handle(self, event):
        try:
            component_registry = self.component_registry
        except (application.NotInitializedError, component.ComponentLookupError):
            logger.warning('Could not lookup component_registry. Not emiting events.')
        else:
            component_registry.handle(event)

    def __enter__(self):
        """Provide with-statement transaction support."""
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        """Provide with-statement transaction support.  If an error occured,
        the transaction is rolled back.  Otherwise, it is committed."""
        
        if exc_type:
            self.rollback()
        else:
            self.commit()

# vim: sw=4:et:ai
