from __future__ import absolute_import

from datetime import datetime
import logging

from dynamodb_mapper.model import (ExpectedValueError, OverwriteError,
    MaxRetriesExceededError, utc_tz, DynamoDBModel)


log = logging.getLogger(__name__)


class TargetNotFoundError(Exception):
    """Raised when attempting to commit a transaction on a target that
    doesn't exist.
    """
    pass


class Transaction(DynamoDBModel):
    """Abstract base class for transactions. Gracefully handles concurrent
    modifications and auto-retries.
    """
    __range_key__ = "datetime"
    # Transient transactions (with this flag set to True) are not saved in the
    # database, and are as a result write-only.
    transient = False

    MAX_RETRIES = 100

    def _setup(self):
        """Set up preconditions and parameters for the transaction.

        This method is only run once, regardless of how many retries happen.
        You should override it to fetch all the *unchanging* information you
        need from the database to run the transaction (e.g. the cost of a Bingo
        card, or the contents of a reward).
        """
        pass

    def _get_target(self):
        """Fetch the object on which this transaction is supposed to operate
        (e.g. a User instance for UserResourceTransactions) from the DB and
        return it.

        It is important that this method actually connect to the database and
        retrieve a clean, up-to-date version of the object -- because it will
        be called repeatedly if conditional updates fail due to the target
        object having changed.

        :raise TargetNotFoundError: If the target doesn't exist in the DB.
        """
        pass

    def _alter_target(self, target):
        """Apply the transaction to the target, modifying it in-place.

        Does *not* attempt to save the target or the transaction to the DB.
        """
        pass

    def _apply_and_save_target(self):
        """Apply the Transaction and attempt to save its target (but not
        the Transaction itself). May be called repeatedly until it stops
        raising :exc:`ExpectedValueError`.

        :raise ExpectedValueError: If the target is changed by an external
            source (other than the Transaction) between its retrieval from
            the DB and the save attempt.
        """
        target = self._get_target()

        # We want to redo the transaction if *anything* in the user
        # changed, not just the target attribute (no accidental overwrites).
        old_values = target.to_db_dict()

        self._alter_target(target)
        target.save(expected_values=old_values)

    def _assign_datetime_and_save(self):
        """Auto-assign a datetime to the Transaction (it's its range key)
        and attempt to save it. May be called repeatedly until it stops raising
        :exc:`OverwriteError`.

        :raise OverwriteError: If there already exists a Transaction with that
            (user_id, datetime) primary key combination.
        """
        self.datetime = datetime.now(utc_tz)
        self.save(allow_overwrite=False)

    def _retry(self, fn, exc_class):
        """Call ``fn`` repeatedly, until it stops raising ``exc_class`` or
        it has been called ``MAX_RETRIES`` times (in which case
        :exc:`MaxRetriesExceededError` is raised).

        :param fn: The callable to retry calling.

        :param exc_class: An exception class (or tuple thereof) that, if raised
            by fn, means it has failed and should be called again.
            *Any other exception will propagate normally, cancelling the
            auto-retry process.*
        """
        tries = 0
        while tries < self.MAX_RETRIES:
            tries += 1
            try:
                fn()
                # Nothing was raised: we're done!
                break
            except exc_class as e:
                log.debug(
                    "%s %s=%s: exception=%s in fn=%s. Retrying (%s).",
                    type(self),
                    self.__hash_key__,
                    getattr(self, self.__hash_key__),
                    e,
                    fn,
                    tries)
        else:
            raise MaxRetriesExceededError()

    def save(self, allow_overwrite=True, expected_values=None):
        """If the transaction is persistent (``transient = False``),
        do nothing.

        If the transaction is transient (``transient = True``), save it to
        the DB, as :meth:`DynamoDBModel.save`.
        """
        cls = type(self)
        if cls.transient:
            log.debug(
                "class=%s: Transient transaction class, ignoring save attempt.",
                cls)
        else:
            super(Transaction, self).save(
                allow_overwrite=allow_overwrite, expected_values=expected_values)

    def commit(self):
        """Commit the transaction:

            - set up preconditions and parameters (:meth:`_setup` -- only called
              once no matter what).
            - fetch the target object in the DB (:meth:`_get_target`).
            - modify the target object according to the transaction's parameters
              (:meth:`_alter_target`).
            - save the (modified) target to the DB
            - save the transaction to the DB

        commit knows how to auto-retry, and uses conditional writes to avoid
        overwriting data in the case of concurrent transactions on the same
        target (see :meth:`_retry`).
        """
        self._setup()

        self._retry(self._apply_and_save_target, ExpectedValueError)
        self._retry(self._assign_datetime_and_save, OverwriteError)
