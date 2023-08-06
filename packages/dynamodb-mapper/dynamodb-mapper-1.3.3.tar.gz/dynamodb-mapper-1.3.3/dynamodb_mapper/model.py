#!/usr/bin/env python
"""Object mapper for Amazon DynamoDB.

Based in part on mongokit's Document interface.

Released under the GNU LGPL, version 3 or later (see COPYING).
"""

import logging
import threading

import boto
from boto.dynamodb.item import Item
from boto.exception import DynamoDBResponseError
import json


log = logging.getLogger(__name__)


MAX_RETRIES = 100


class SchemaError(Exception):
    """Raised when a DynamoDBModel class's schema is incorrect."""
    pass


class MaxRetriesExceededError(Exception):
    """Raised when a failed operation couldn't be completed after retrying
    MAX_RETRIES times (e.g. saving an autoincrementing hash_key).
    """
    pass


class OverwriteError(Exception):
    """Raised when saving a DynamoDBModel instance would overwrite something
    in the database and we've forbidden that because we believe we're creating
    a new one (see :meth:`DynamoDBModel.save`).
    """
    pass


class ExpectedValueError(Exception):
    """Conditional write failure.
    Raised when the expected_values argument to :meth:`DynamoDBModel.save`
    doesn't match what is stored in the database (i.e. when somebody changed
    the DB's version of your object behind your back).
    """
    pass


class autoincrement_int(int):
    """Dummy int subclass for use in your schemas.

    If you're using this class as the type for your key in a hash_key-only
    table, new objects in your table will have an auto-incrementing primary
    key.

    Note that you can still insert items with explicit values for your primary
    key -- the autoincrementing scheme is only used for objects with unset
    hash_keys (or to be more precise, left set to the default value of 0).

    Auto-incrementing int keys are implemented by storing a special "magic"
    item in the table with the following properties:
      - hash_key_value = 0
      - __max_hash_key__ = X
    where X is the maximum used hash_key value.

    Inserting a new item issues a conditional write to the magic item,
    incrementing __max_hash_key__ iff it hasn't changed and using that new
    value for the created object's hash_key value.
    """
    pass


class json_list(list):
    """JSON-serialized list data type for use in your schemas.

    From your object's point of view, it's a list with arbitrary nesting and
    whatever you want to store in it.

    In DynamoDB itself, though, it's stored as a JSON-serialized string.
    """
    def __init__(self, source_str=""):
        if source_str:
            super(json_list, self).__init__(json.loads(source_str))
        else:
            super(json_list, self).__init__()


class json_dict(dict):
    """JSON-serialized dict data type for use in your schemas.

    From your object's point of view, it's a dict with arbitrary nesting and
    whatever you want to store in it.

    In DynamoDB itself, though, it's stored as a JSON-serialized string.
    """
    def __init__(self, source_str=""):
        if source_str:
            super(json_dict, self).__init__(json.loads(source_str))
        else:
            super(json_dict, self).__init__()


_JSON_TYPES = frozenset([json_list, json_dict])


class ConnectionBorg(object):
    """Borg that handles access to DynamoDB.

    You should never make any explicit/direct boto.dynamodb calls by yourself.

    Remember to call :meth:`set_auth_credentials`, or to set the
    ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY`` environment variables
    before making any calls.
    """
    _shared_state = {
        "_aws_access_key_id": None,
        "_aws_secret_access_key": None,
        # {thread_id: connection} mapping
        "_connections": {},
    }

    def __init__(self):
        self.__dict__ = self._shared_state

    def _get_connection(self):
        """Return the DynamoDB connection for the current thread, establishing
        it if required.
        """
        current_thread = threading.current_thread()
        thread_id = current_thread.ident
        try:
            return self._connections[thread_id]
        except KeyError:
            log.debug("Creating DynamoDB connection for thread %s.", current_thread)
            self._connections[thread_id] = boto.connect_dynamodb(
                aws_access_key_id=self._aws_access_key_id,
                aws_secret_access_key=self._aws_secret_access_key
            )
            return self._connections[thread_id]

    def _create_autoincrement_magic_item(self, table):
        item = table.new_item(hash_key=0, attrs={
            "__max_hash_key__": 0
        })
        # Conditional write: don't risk overwriting the DB.
        item.put({item.hash_key_name: False})

    def set_credentials(self, aws_access_key_id, aws_secret_access_key):
        """Set the DynamoDB credentials."""
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key

    def create_table(self, cls, read_units, write_units, wait_for_active=False):
        """Create a table that'll be used to store instances of cls.

        See `http://docs.amazonwebservices.com/amazondynamodb/latest/developerguide/ProvisionedThroughputIntro.html`_
        for information about provisioned throughput.

        :param cls: The class whose instances will be stored in the table.

        :param read_units: The number of read units to provision for this table
            (minimum 5)

        :param write_units: The number of write units to provision for this
            table (minimum 5).

        :param wait_for_active: If True, create_table will wait for the table
            to become ACTIVE before returning (otherwise, it'll be CREATING).
            Note that this can take up to a minute.
            Defaults to False.
        """
        table_name = cls.__table__
        hash_key_name = cls.__hash_key__
        range_key_name = cls.__range_key__

        if not table_name:
            raise SchemaError("Class does not define __table__", cls)

        if not hash_key_name:
            raise SchemaError("Class does not define __hash_key__", cls)

        if not cls.__schema__:
            raise SchemaError("Class does not define __schema__", cls)

        hash_key_type = cls.__schema__[hash_key_name]

        if hash_key_type == autoincrement_int:
            if range_key_name:
                raise SchemaError(
                    "Class defines both a range key and an autoincrement_int hash key",
                    cls)
            if not wait_for_active:
                # Maybe we should raise ValueError instead?
                log.info(
                    "Class %s has autoincrement_int hash key -- forcing wait_for_active",
                    cls)
                wait_for_active = True

        conn = self._get_connection()
        # It's a prototype/an instance, not a type.
        hash_key_proto_value = hash_key_type()
        # None in the case of a hash-only table.
        if range_key_name:
            # We have a range key, its type must be specified.
            range_key_proto_value = cls.__schema__[range_key_name]()
        else:
            range_key_proto_value = None

        schema = conn.create_schema(
            hash_key_name=hash_key_name,
            hash_key_proto_value=hash_key_proto_value,
            range_key_name=range_key_name,
            range_key_proto_value=range_key_proto_value
        )
        table = conn.create_table(cls.__table__, schema, read_units, write_units)
        table.refresh(wait_for_active=wait_for_active)

        if hash_key_type == autoincrement_int:
            self._create_autoincrement_magic_item(table)

        return table

    def get_table(self, name):
        """Return the table with the requested name."""
        return self._get_connection().get_table(name)

    def new_batch_list(self):
        """Create a new batch list."""
        return self._get_connection().new_batch_list()


class DynamoDBModel(object):
    """Abstract base class for all models that use DynamoDB as their storage
    backend.

    Each subclass must define the following attributes:

      - __table__: the name of the table used for storage.
      - __hash_key__: the name of the primary hash key.
      - __range_key__: (optional) if you're using a composite primary key,
          the name of the range key.
      - __schema__: {attribute_name: attribute_type} mapping.
          Supported attribute_types are: int, long, float, str, unicode, set.
          Default values are obtained by calling the type with no args
          (so 0 for numbers, "" for strings and empty sets).

    To redefine serialization/deserialization semantics (e.g. to have more
    complex schemas, like auto-serialized JSON data structures), override the
    from_dict (deserialization) and to_db_dict (serialization) methods.

    *Important implementation note regarding sets:* DynamoDB can't store empty
    sets/strings. Therefore, since we have schema information available to us,
    we're storing empty sets/strings as missing attributes in DynamoDB, and
    converting back and forth based on the schema.

    So if your schema looks like the following: {"id": unicode, "name" str,
    "cheats": set}, then {"id": "e1m1", "name": "Hangar",
    "cheats": set(["idkfa", "iddqd"])} will be stored exactly as is, but
    {"id": "e1m2", "name": "", "cheats": set()} will be stored as simply
    {"id": "e1m2"}


    TODO Add checks for common error cases:
        - Wrong datatypes in the schema
        - hash_key/range_key incorrectly defined

    TODO Add consistent/eventually consistent reads flag.
    """

    # TODO Add checks to the various methods so that meaningful error messages
    # are raised when they're incorrectly overridden.
    __table__ = None
    __hash_key__ = None
    __range_key__ = None
    __schema__ = None

    @classmethod
    def from_dict(cls, d):
        """Build an instance from a dict-like mapping,
        according to the class's schema.

        Default values are used for anything that's missing from the dict
        (see DynamoDBModel class docstring).
        """
        instance = cls()
        for (name, type_) in cls.__schema__.iteritems():
            try:
                value = type_(d[name])
            except KeyError:
                # Fill in missing attributes with default values.
                value = type_()
            setattr(instance, name, value)
        return instance

    @classmethod
    def get(cls, hash_key_value, range_key_value=None):
        """Retrieve a single object from DynamoDB according to its primary key.

        Note that this is not a query method -- it will only return the object
        matching the exact primary key provided. Meaning that if the table is
        using a composite primary key, you need to specify both the hash and
        range key values.
        """
        table = ConnectionBorg().get_table(cls.__table__)
        return cls.from_dict(
            table.get_item(hash_key=hash_key_value, range_key=range_key_value))

    @classmethod
    def get_batch(cls, keys):
        """Retrieve multiple objects according to their primary keys.

        Like get, this isn't a query method -- you need to provide the exact
        primary key(s) for each object you want to retrieve:

          - If the primary keys are hash keys, keys must be a list of
            their values (e.g. [1, 2, 3, 4]).
          - If the primary keys are composite (hash + range), keys must
            be a list of (hash_key, range_key) values
            (e.g. [("user1", 1), ("user1", 2), ("user1", 3)]).
        """
        borg = ConnectionBorg()
        table = borg.get_table(cls.__table__)
        batch_list = borg.new_batch_list()
        batch_list.add_batch(table, keys)

        res = batch_list.submit()
        return [
            cls.from_dict(d) for d in res[u"Responses"][cls.__table__][u"Items"]
        ]

    @classmethod
    def query(cls, hash_key_value, range_key_condition=None):
        """Query DynamoDB for items matching the requested key criteria.

        You need to supply an exact hash key value, and optionally, conditions
        on the range key. If no such conditions are supplied, all items matching
        the hash key value will be returned.

        This method can only be used on tables with composite (hash + range)
        primary keys -- since the exact hash key value is mandatory, on tables
        with hash-only primary keys, cls.get(k) does the same thing cls.query(k)
        would.

        :param hash_key_value: The hash key's value for all requested items.

        :param range_key_condition: A condition instance from
            boto.dynamodb.condition -- one of EQ(x), LE(x), LT(x), GE(x),
            GT(x), BEGINS_WITH(x), BETWEEN(x, y).
        """
        table = ConnectionBorg().get_table(cls.__table__)
        return [
            cls.from_dict(d)
            for d in table.query(hash_key_value, range_key_condition)
        ]

    @classmethod
    def scan(cls, scan_filter=None):
        """Scan DynamoDB for items matching the requested criteria.

        You can scan based on any attribute and any criteria (including multiple
        criteria on multiple attributes), not just the primary keys.

        Scan is a very expensive operation -- it doesn't use any indexes and will
        look through the entire table. As much as possible, you should avoid it.

        :param scan_filter: A {attribute_name: condition} dict, where
            condition is a condition instance from boto.dynamodb.condition.
        """
        table = ConnectionBorg().get_table(cls.__table__)
        return [
            cls.from_dict(d)
            for d in table.scan(scan_filter)
        ]

    def __init__(self):
        """Create a default empty instance of the class with default values
        according to its schema.

        We're supplying this method to avoid the need for extra checks in save.
        """
        for (name, type_) in type(self).__schema__.iteritems():
            setattr(self, name, type_())

    def to_db_dict(self):
        """Return a dict representation of the object according to the class's
        schema, suitable for direct storage in DynamoDB.
        """
        out = {}
        for (name, type_) in type(self).__schema__.iteritems():
            value = getattr(self, name)
            if type_ in _JSON_TYPES:
                # json serialization hooks for json_* data types.
                out[name] = json.dumps(value, sort_keys=True)
            elif value or value == 0:
                # Yes, that part is horrible. DynamoDB can't store empty
                # sets/strings, so we're representing them as missing
                # attributes on the DB side.
                out[name] = value
        return out

    def to_json_dict(self):
        """Return a dict representation of the object, suitable for JSON
        serialization.

        This means the values must all be valid JSON object types
        (in particular, sets must be converted to lists), but types not
        suitable for DynamoDB (e.g. nested data structures) may be used.

        Note that this method is never used for interaction with the database
        (:meth:`to_db_dict` is).
        """
        out = {}
        for name in self.__schema__:
            value = getattr(self, name)
            if isinstance(value, (set, frozenset)):
                out[name] = list(value)
            else:
                out[name] = value
        return out

    def _save_autoincrement_hash_key(self, item):
        """Compute an autoincremented hash_key for an item and save it to the DB.

        TODO Add schema checks.
        """
        tries = 0
        while tries < MAX_RETRIES:
            tries += 1
            max_hash_item = item.table.get_item(0, consistent_read=True)
            max_hash_key = max_hash_item["__max_hash_key__"]
            max_hash_item["__max_hash_key__"] += 1
            try:
                # Conditional write: we're overwriting iff the value
                # hasn't changed.
                max_hash_item.put({"__max_hash_key__": max_hash_key})
                # We just reserved that value for the hash key
                item[item.hash_key_name] = max_hash_key + 1
                # If despite our checks someone manually inserted an item at
                # that primary key, we'll retry with the next available value.
                item.put({item.hash_key_name: False})
                break
            except DynamoDBResponseError as e:
                if e.error_code != "ConditionalCheckFailedException":
                    # Unhandled exception
                    raise
                log.debug(
                    "table=%s, max hash key has changed. Retrying (%s).",
                    item.table, tries)
        else:
            raise MaxRetriesExceededError()

    def save(self, allow_overwrite=True, expected_values=None):
        """Save the object to the database.

        This method may be used both to insert a new object in the DB, or to
        update an existing one (iff allow_overwrite == True).

        :param allow_overwrite: If False, the method will only succeed if this
            object's primary keys don't exist in the database (otherwise,
            :class:`OverwriteError` is raised).

        :param expected_values: dict of expected attribute values -- if any
            one of these values doesn't match what is in the database
            (i.e. someone went ahead and modified the object in the DB behind
            your back), the operation fails and raises
            :class:`ExpectedValueError`.
        """
        if expected_values is None:
            expected_values = {}

        cls = type(self)
        schema = cls.__schema__
        hash_key = cls.__hash_key__
        range_key = cls.__range_key__
        table = ConnectionBorg().get_table(cls.__table__)
        item_data = self.to_db_dict()
        item = Item(table, attrs=item_data)

        if schema[hash_key] == autoincrement_int and item_data[hash_key] == 0:
            # We're inserting a new item in an autoincrementing table.
            self._save_autoincrement_hash_key(item)
            # Update the primary key so that it reflects what it was saved as.
            setattr(self, hash_key, item[hash_key])
        else:
            if allow_overwrite:
                expected_db_values = {}
                schema = type(self).__schema__
                for (name, value) in expected_values.iteritems():
                    type_ = schema[name]
                    # This bit can probably be factored out with to_db_dict
                    if type_ in _JSON_TYPES:
                        expected_db_values[name] = json.dumps(value, sort_keys=True)
                    elif value or value == 0:
                        expected_db_values[name] = value
                    else:
                        # Empty strings/sets must be represented as missing values
                        expected_db_values[name] = False
            else:
                # Forbid overwrites: do a conditional write on
                # "this hash_key doesn't exist"
                expected_db_values = {hash_key: False}
                if range_key:
                    expected_db_values[range_key] = False
            try:
                item.put(expected_db_values)
            except DynamoDBResponseError as e:
                if e.error_code == "ConditionalCheckFailedException":
                    if allow_overwrite:
                        # Failed conditional write
                        raise ExpectedValueError(item)
                    # Forbidden overwrite
                    raise OverwriteError(item)
                # Unhandled exception
                raise

    def delete(self):
        """Delete the current object from the database."""
        cls = type(self)
        hash_key_value = getattr(self, cls.__hash_key__)
        # Range key is only present in composite primary keys
        if cls.__range_key__:
            range_key_value = getattr(self, cls.__range_key__)
        else:
            range_key_value = None

        table = ConnectionBorg().get_table(cls.__table__)
        Item(table, hash_key_value, range_key_value).delete()
