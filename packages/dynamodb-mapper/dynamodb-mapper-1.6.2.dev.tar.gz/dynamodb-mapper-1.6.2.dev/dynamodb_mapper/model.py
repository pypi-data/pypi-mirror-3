"""Object mapper for Amazon DynamoDB.

Based in part on mongokit's Document interface.

Released under the GNU LGPL, version 3 or later (see COPYING).
"""
from __future__ import absolute_import

import json
import logging
import threading
from datetime import datetime, timedelta, tzinfo

import boto
from boto.dynamodb.item import Item
from boto.exception import DynamoDBResponseError


log = logging.getLogger(__name__)
dblog = logging.getLogger(__name__+".database-access")


MAX_RETRIES = 100
# primary key of the magic item used for autoinc
MAGIC_KEY = -1

class SchemaError(Exception):
    """Raised when a DynamoDBModel class's schema is incorrect."""
    pass


class ThroughputError(Exception):
    """Raised when reaquested throughput can not be allocated."""
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
      - hash_key_value = -1
      - __max_hash_key__ = X
    where X is the maximum used hash_key value.

    Inserting a new item issues an atomic add on the '__max_hash_key__' value.
    Its new value is returned and used as the primary key for the new elem.

    Note that hash_key_value is set to '-1' while '__max_hash_key__' initial
    value is 0. This will element at key '0' unused. It's actually a garbage item
    for cases where a value is manually added to an unitialized index.
    """
    pass


_JSON_TYPES = frozenset([list, dict])


class UTC(tzinfo):
    """UTC timezone"""
    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)


utc_tz = UTC()


def _get_proto_value(schema_type):
    """Return a prototype value matching what schema_type will be serialized
    as in DynamoDB:

      - For strings and numbers, an instance of schema_type.
      - For "special" types implemented at the mapper level (list, dict,
        datetime), an empty string (this is what they're stored as in the DB).
    """
    # Those types must be serialized as strings
    if schema_type in _JSON_TYPES:
        return u""

    if schema_type is datetime:
        return u""

    # Regular string/number
    return schema_type()


def _get_default_value(schema_type, default=None):
    """Return a default value matching schema_type or default if provided:

      - For datetime.datetime, it's NOW.
      - For container types, it's an empty container.
      - For strings, it's an empty string.
      - For numbers, it's zero.

      This function may raise TypeError exception if:
       - default was callable and required arguments
       - default or its return value is not an instance of schema_type

      :param schema_type class object to instanciate
      :param default default value. May be a value or a callable (functions, class, ...) It must *NOT* require an any argument and it's type must match schema_type

    """
    if default is not None:
        # If default is callable(function, constructor, ...), try to dereference it
        if hasattr(default, '__call__'):
            # Might raise a "TypeError" if arguments were needed
            default = default()
        # Check default value consitency
        if not isinstance(default, schema_type):
            raise TypeError("Expected default value of type {}, got: {}".format(schema_type, type(default)))
        else:
            return default

    if schema_type is datetime:
        # Current Timestamp
        return datetime.now(tz=utc_tz)

    return schema_type()


def _python_to_dynamodb(value):
    """Convert a Python object to a representation suitable to direct storage
    in DynamoDB, according to a type from a DynamoDBModel schema.

    If value should be represented as a missing value in DynamoDB
    (empty string or set), None is returned.

    ``_dynamodb_to_python(t, _python_to_dynamodb(v)) == v`` for any v.

    :param value: The Python object to convert.

    :return: ``value``, serialized to DynamoDB, or ``None`` if ``value`` must
        be represented as a missing attribute.
    """
    if isinstance(value, tuple(_JSON_TYPES)):
        # json serialization hooks for json_* data types.
        return json.dumps(value, sort_keys=True)

    if isinstance(value, datetime):
        # datetime instances are stored as UTC in the DB itself.
        # (that way, they become sortable)
        # datetime objects without tzinfo are not supported.
        s = value.astimezone(utc_tz).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        # there is not strftime code to output the timezone with the ':' that
        # is mandated by the W3CDTF format, so here's an ugly hack
        s = s[:-2] + ':' + s[-2:]
        return s

    # This case prevents `'fields': False` to be added when genereating expected
    # values dict in save as this would mean 'field does not exist' instead of
    # 'field exists and is False'.
    if isinstance(value, bool):
        return int(value)

    if value or value == 0:
        return value

    # Yes, that part is horrible. DynamoDB can't store empty
    # sets/strings, so we're representing them as missing
    # attributes on the DB side.
    return None


def _dynamodb_to_python(schema_type, value):
    """Convert a DynamoDB attribute value to a Python object, according to a
    type from a DynamoDBModel schema.

    If value is None (usually because the attribute was missing in the first
    place), a default value is returned (empty string or set, or 0, depending
    on what the type is).

    ``_dynamodb_to_python(t, _python_to_dynamodb(v)) == v`` for any v.

    :param schema_type: A type supported by the mapper (TODO Clearly list those).

    :param value: The DynamoDB attribute to convert to a Python object.
        May be ``None``.

    :return: An instance of ``schema_type``.
    """
    # This means a missing attribute for a _JSON_TYPES object is valid,
    # and results in an empty sequence. Is that a bad thing?
    if value is None:
        return None

    if schema_type in _JSON_TYPES:
        return schema_type(json.loads(value))

    if schema_type is datetime:
        # Parse TZ-aware isoformat

        # strptime doesn't support timezone parsing (%z flag), so we're forcing
        # the strings in the database to be UTC (+00:00) for now.
        # TODO Handle arbitrary timezones (with manual parsing).
        if value.endswith('Z'):
            value = value[:-2] + '+00:00'
        return datetime.strptime(
            value, "%Y-%m-%dT%H:%M:%S.%f+00:00").replace(tzinfo=utc_tz)

    return schema_type(value)


class ConnectionBorg(object):
    """Borg that handles access to DynamoDB.

    You should never make any explicit/direct boto.dynamodb calls by yourself
    except for table maintenance operations :
    * boto.dynamodb.table.update_throughput()
    * boto.dynamodb.table.delete()

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
        item = table.new_item(hash_key=MAGIC_KEY, attrs={
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

        if read_units < 5 or write_units < 5:
            raise ThroughputError("Either read or write throughput is below 5")

        hash_key_type = cls.__schema__[hash_key_name]

        if hash_key_type is autoincrement_int:
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
        hash_key_proto_value = _get_proto_value(hash_key_type)
        # None in the case of a hash-only table.
        if range_key_name:
            # We have a range key, its type must be specified.
            range_key_proto_value = _get_proto_value(
                cls.__schema__[range_key_name])
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

        if hash_key_type is autoincrement_int:
            self._create_autoincrement_magic_item(table)

        dblog.debug("Created table %s(%s, %s)", cls.__table__, hash_key_name, range_key_name)

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
      - __defaults__: {attribute_name: defaulter} optional mapping.
          This dict allows to provide a default value for each attribute_name at
          object creation time. It will *never* be used when loading from the DB.
          It is fully optional. If no value is supplied the empty value
          corresponding to the type will be used.
          "defaulter" may either be a scalar value or a callable with no
          arguments.

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
    """

    # TODO Add checks to the various methods so that meaningful error messages
    # are raised when they're incorrectly overridden.
    __table__ = None
    __hash_key__ = None
    __range_key__ = None
    __schema__ = None
    __defaults__ = {}

    def __init__(self, **kwargs):
        """Create an instance of the model. All fields defined in the schema
        are created. By order of prioritym its value will be loaded from:

        * kwargs
        * __default__
        * mapper's default (0, empty string, empty set, ...)

        We're supplying this method to avoid the need for extra checks in save and
        ease object initial creation.
        """
        defaults = type(self).__defaults__
        schema = type(self).__schema__

        for (name, type_) in schema.iteritems():
            if name in kwargs:
                default = kwargs.get(name)
            else:
                default = defaults[name] if name in defaults else None
            setattr(self, name, _get_default_value(type_, default))

    @classmethod
    def from_dict(cls, d):
        """Build an instance from a dict-like mapping,
        according to the class's schema.

        Default values are used for anything that's missing from the dict
        (see DynamoDBModel class docstring).
        """
        #FIXME: rename to from_db_dict when breaking compat or disambiguing
        instance = cls()
        for (name, type_) in cls.__schema__.iteritems():
            # Set the value if we got one from DynamoDB. Otherwise, stick with the default
            value = _dynamodb_to_python(type_, d.get(name))
            if value is None:
                value = _get_default_value(type_)
            setattr(instance, name, value)
        return instance

    @classmethod
    def get(cls, hash_key_value, range_key_value=None, consistent_read=False):
        """Retrieve a single object from DynamoDB according to its primary key.

        Note that this is not a query method -- it will only return the object
        matching the exact primary key provided. Meaning that if the table is
        using a composite primary key, you need to specify both the hash and
        range key values.

        :param hash_key_value: The value of the requested item's hash_key.

        :param range_key_value: The value of the requested item's range_key,
            if the table has a composite key.

        :param consistent_read: If False (default), an eventually consistent
            read is performed. Set to True for strongly consistent reads.
        """
        table = ConnectionBorg().get_table(cls.__table__)
        # Convert the keys to DynamoDB values.
        h_value = _python_to_dynamodb(hash_key_value)
        if cls.__range_key__:
            r_value = _python_to_dynamodb(range_key_value)
        else:
            r_value = None

        item = table.get_item(
                    hash_key=h_value,
                    range_key=r_value,
                    consistent_read=consistent_read)

        dblog.debug("Got item (%s, %s) from table %s", h_value, r_value, cls.__table__)

        return cls.from_dict(item)

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

        get_batch *always* performs eventually consistent reads.

        Please not that a batch can *not* read more than 100 items at once.
        """
        if len(keys) > 100:
            raise ValueError("Too many items to read in a single batch. Maximum is 100.")

        borg = ConnectionBorg()
        table = borg.get_table(cls.__table__)
        # Convert all the keys to DynamoDB values.
        if cls.__range_key__:
            dynamo_keys = [
                (
                    _python_to_dynamodb(h),
                    _python_to_dynamodb(r)
                ) for (h, r) in keys
            ]
        else:
            dynamo_keys = map(_python_to_dynamodb, keys)

        batch_list = borg.new_batch_list()
        batch_list.add_batch(table, dynamo_keys)

        res = batch_list.submit()

        dblog.debug("Sent a batch get on table %s", cls.__table__)

        return [
            cls.from_dict(d) for d in res[u"Responses"][cls.__table__][u"Items"]
        ]

    @classmethod
    def query(cls, hash_key_value, range_key_condition=None, consistent_read=False, reverse=False):
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

        :param consistent_read: If False (default), an eventually consistent
            read is performed. Set to True for strongly consistent reads.

        :rtype: generator
        """
        table = ConnectionBorg().get_table(cls.__table__)
        h_value = _python_to_dynamodb(hash_key_value)

        res = table.query(
                h_value,
                range_key_condition,
                consistent_read=consistent_read,
                scan_index_forward=not reverse)

        dblog.debug("Queried (%s, %s) on table %s", h_value, range_key_condition, cls.__table__)

        return (cls.from_dict(d) for d in res)

    @classmethod
    def scan(cls, scan_filter=None):
        """Scan DynamoDB for items matching the requested criteria.

        You can scan based on any attribute and any criteria (including multiple
        criteria on multiple attributes), not just the primary keys.

        Scan is a very expensive operation -- it doesn't use any indexes and will
        look through the entire table. As much as possible, you should avoid it.

        :param scan_filter: A {attribute_name: condition} dict, where
            condition is a condition instance from boto.dynamodb.condition.

        :rtype: generator
        """
        table = ConnectionBorg().get_table(cls.__table__)
        hash_key_name = table.schema.hash_key_name

        res = table.scan(scan_filter)

        dblog.debug("Scanned table %s with filter %s", cls.__table__, scan_filter)

        return (
            cls.from_dict(d)
            for d in res
            if d[hash_key_name] != MAGIC_KEY or cls.__schema__[hash_key_name] != autoincrement_int
        )

    def to_db_dict(self):
        """Return a dict representation of the object according to the class's
        schema, suitable for direct storage in DynamoDB.
        """
        out = {}
        for name in type(self).__schema__:
            value = _python_to_dynamodb(getattr(self, name))
            if value is not None:
                # DynamoDB can't store empty sets/strings, so we must
                # represent them as missing attributes
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
                out[name] = sorted(value)
            elif isinstance(value, datetime):
                # Using strftime instead of str or isoformat to get the right
                # separator ('T') and time offset notation (with ':')
                out[name] = value.astimezone(utc_tz).isoformat()
            else:
                out[name] = value
        return out

    def _save_autoincrement_hash_key(self, item):
        """Compute an autoincremented hash_key for an item and save it to the DB.

        To achieve this goal, we keep a special object at hash_key=0 to keep track
        of the counter status. We then issue an atomic inc to the counter field.
        We do not need to read it befor as we know its hesh_key yet.
        The new value is send back to us and used as the hash_key for elem
        """
        counter_key = '__max_hash_key__'
        tries = 0

        while tries < MAX_RETRIES:
            tries += 1
            # Create a 'new item' with key=0 and trigger an atomic increment
            # This spares one read unit :)
            max_hash_item = item.table.new_item(MAGIC_KEY)
            max_hash_item.add_attribute(counter_key, 1)
            max_hash_item = max_hash_item.save(return_values='ALL_NEW')
            # We just reserved that value for the hash key
            item[item.hash_key_name] = max_hash_item['Attributes'][counter_key]

            try:
                # Make sure this primary key was not 'stolen' by a direct DB access
                item.put({item.hash_key_name: False})
                return
            except DynamoDBResponseError as e:
                if e.error_code != "ConditionalCheckFailedException":
                    # Unhandled exception
                    raise
                log.debug(
                    "table=%s, An item seems to have been manually inserted at index %s (%s).",
                    item.table, item[item.hash_key_name], tries)

        # This table auto-incr has been screwed up...
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

        # Detect magic elem manual overwrite
        if schema[hash_key] == autoincrement_int and item_data[hash_key] == MAGIC_KEY:
            raise SchemaError()
        # We're inserting a new item in an autoincrementing table.
        if schema[hash_key] == autoincrement_int and item_data[hash_key] == 0:
            # Compute the index and save the object
            self._save_autoincrement_hash_key(item)
            # Update the primary key so that it reflects what it was saved as.
            setattr(self, hash_key, item[hash_key])
        # Regular save
        else:
            if allow_overwrite:
                expected_db_values = {}
                schema = type(self).__schema__
                for (name, value) in expected_values.iteritems():
                    db_value = _python_to_dynamodb(value)
                    if db_value is None:
                        # Empty strings/sets must be represented as missing values
                        expected_db_values[name] = False
                    else:
                        expected_db_values[name] = db_value
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

        hash_key_value = getattr(self, hash_key)
        range_key_value = getattr(self, hash_key, None)
        dblog.debug("Saved (%s, %s) in table %s allow_overwrite=%s", hash_key_value, range_key_value, cls.__table__, allow_overwrite)

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

        dblog.debug("Deleted (%s, %s) from table %s", hash_key_value, range_key_value, cls.__table__)
