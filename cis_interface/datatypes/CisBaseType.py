import copy
import json
import jsonschema
from cis_interface import backwards


class CisTypeError(TypeError):
    r"""Error that should be raised when a class encounters a type it cannot handle."""
    pass


class CisBaseType(object):
    r"""Base type that should be subclassed by user defined types. Attributes
    should be overwritten to match the type.

    Arguments:
        **kwargs: All keyword arguments are assumed to be type definition
            properties which will be used to validate serialized/deserialized
            messages.

    Attributes:
        name (str): Name of the type for use in YAML files & form options.
        description (str): A short description of the type.
        properties (dict): JSON schema definitions for properties of the
            type.
        definition_properties (list): Type properties that are required for YAML
            or form entries specifying the type. These will also be used to
            validate type definitions.
        metadata_properties (list): Type properties that are required for
            deserializing instances of the type that have been serialized.
        data_schema (dict): JSON schema for validating a JSON friendly
            representation of the type.

    """

    name = 'base'
    description = 'A generic base type for users to build on.'
    properties = {}
    definition_properties = []
    metadata_properties = []
    data_schema = {'description': 'JSON friendly version of type instance.',
                   'type': 'string'}
    _empty_msg = {}
    sep = backwards.unicode2bytes(':CIS_TAG:')

    def __init__(self, **typedef):
        self._typedef = {}
        typedef.setdefault('typename', self.name)
        self.update_typedef(**typedef)

    # Methods to be overridden by subclasses
    @classmethod
    def encode_type(cls, obj):
        r"""Encode an object's type definition.

        Args:
            obj (object): Object to encode.

        Raises:
            CisTypeError: If the object is not the correct type.

        Returns:
            dict: Encoded type definition.

        """
        raise NotImplementedError("Method must be overridden by the subclass.")

    @classmethod
    def encode_data(cls, obj, typedef):
        r"""Encode an object's data.

        Args:
            obj (object): Object to encode.
            typedef (dict): Type definition that should be used to encode the
                object.

        Returns:
            string: Encoded object.

        """
        raise NotImplementedError("Method must be overridden by the subclass.")

    @classmethod
    def decode_data(cls, obj, typedef):
        r"""Decode an object.

        Args:
            obj (string): Encoded object to decode.
            typedef (dict): Type definition that should be used to decode the
                object.

        Returns:
            object: Decoded object.

        """
        raise NotImplementedError("Method must be overridden by the subclass.")

    @classmethod
    def transform_type(cls, obj, typedef=None):
        r"""Transform an object based on type info.

        Args:
            obj (object): Object to transform.
            typedef (dict): Type definition that should be used to transform the
                object.

        Returns:
            object: Transformed object.

        """
        raise NotImplementedError("Method must be overridden by the subclass.")

    # Methods not to be modified by subclasses
    @classmethod
    def extract_typedef(cls, metadata):
        r"""Extract the minimum typedef required for this type from the provided
        metadata.

        Args:
            metadata (dict): Message metadata.

        Returns:
            dict: Encoded type definition with unncessary properties removed.

        """
        out = copy.deepcopy(metadata)
        reqkeys = cls.definition_schema()['required']
        keylist = [k for k in out.keys()]
        for k in keylist:
            if k not in reqkeys:
                del out[k]
        cls.validate_definition(out)
        return out

    def update_typedef(self, **kwargs):
        r"""Update the current typedef with new values.

        Args:
            **kwargs: All keyword arguments are considered to be new type
                definitions. If they are a valid definition property, they
                will be copied to the typedef associated with the instance.

        Returns:
            dict: A dictionary of keyword arguments that were not added to the
                type definition.

        Raises:
            CisTypeError: If the current type does not match the type being
                updated to.

        """
        typename0 = self._typedef.get('typename', None)
        typename1 = kwargs.get('typename', None)
        # Check typename to make sure this is possible
        if typename1 and typename0 and (typename1 != typename0):
            raise CisTypeError("Cannot update typedef for type '%s' to be '%s'."
                               % (typename0, typename1))
        # Copy over valid properties
        definition_schema = self.__class__.definition_schema()
        all_keys = [k for k in kwargs.keys()]
        for k in all_keys:
            if k in definition_schema['properties']:
                self._typedef[k] = kwargs.pop(k)
        # Validate
        self.__class__.validate_definition(self._typedef)
        return kwargs

    @classmethod
    def definition_schema(cls):
        r"""JSON schema for validating a type definition."""
        out = {"$schema": "http://json-schema.org/draft-07/schema#",
               'title': cls.name,
               'description': cls.description,
               'type': 'object',
               'required': copy.deepcopy(cls.definition_properties),
               'properties': copy.deepcopy(cls.properties)}
        out['required'] += ['typename']
        out['properties']['typename'] = {
            'description': 'Name of the type encoded.',
            'type': 'string',
            'enum': [cls.name]}
        return out

    @classmethod
    def metadata_schema(cls):
        r"""JSON schema for validating a JSON serialization of the type."""
        out = cls.definition_schema()
        out['required'] = copy.deepcopy(cls.metadata_properties)
        out['required'] += ['typename']
        return out

    @classmethod
    def validate_metadata(cls, obj):
        r"""Validates an encoded object.

        Args:
            obj (string): Encoded object to validate.

        """
        jsonschema.validate(obj, cls.metadata_schema())

    @classmethod
    def validate_definition(cls, obj):
        r"""Validates a type definition.

        Args:
            obj (object): Type definition to validate.

        """
        jsonschema.validate(obj, cls.definition_schema())

    @classmethod
    def check_meta_compat(cls, k, v1, v2):
        r"""Check that two metadata values are compatible.

        Args:
            k (str): Key for the entry.
            v1 (object): Value 1.
            v2 (object): Value 2.

        Returns:
            bool: True if the two entries are compatible going from v1 to v2,
                False otherwise.

        """
        return (v1 == v2)

    @classmethod
    def check_encoded(cls, metadata, typedef=None):
        r"""Checks if the metadata for an encoded object matches the type
        definition.

        Args:
            metadata (dict): Meta data to be tested.
            typedef (dict, optional): Type properties that object should
                be tested against. Defaults to None and object may have
                any values for the type properties (so long as they match
                the schema.

        Returns:
            bool: True if the metadata matches the type definition, False
                otherwise.

        """
        try:
            cls.validate_metadata(metadata)
        except jsonschema.exceptions.ValidationError:
            return False
        if typedef is not None:
            try:
                cls.validate_definition(typedef)
            except jsonschema.exceptions.ValidationError:
                return False
            for k, v in typedef.items():
                if not cls.check_meta_compat(k, metadata.get(k, None), v):
                    # print("Incompatible elements: ", k)
                    # print("    1.", metadata.get(k, None))
                    # print("    2.", v)
                    return False
        return True

    @classmethod
    def check_decoded(cls, obj, typedef=None):
        r"""Checks if an object is of the this type.

        Args:
            obj (object): Object to be tested.
            typedef (dict): Type properties that object should be tested
                against. If None, this will always return True.

        Returns:
            bool: Truth of if the input object is of this type.

        """
        try:
            datadef = cls.encode_type(obj)
            datadef['typename'] = cls.name
        except CisTypeError:
            # print('CisTypeError in check_decoded', type(obj), obj)
            return False
        return cls.check_encoded(datadef, typedef)

    @classmethod
    def encode(cls, obj, typedef=None):
        r"""Encode an object.

        Args:
            obj (object): Object to encode.
            typedef (dict, optional): Type properties that object should
                be tested against. Defaults to None and object may have
                any values for the type properties (so long as they match
                the schema.

        Returns:
            tuple(dict, bytes): Encoded object with type definition and data
                serialized to bytes.

        Raises:
            ValueError: If the object does not match the type definition.
            ValueError: If the encoded metadata does not match the type
                definition.
            TypeError: If the encoded data is not of bytes type.

        """
        # This is slightly redundent, maybe pass None
        if not cls.check_decoded(obj, typedef):
            raise ValueError("Object is not correct type for encoding.")
        obj_t = cls.transform_type(obj, typedef)
        metadata = cls.encode_type(obj_t)
        metadata['typename'] = cls.name
        data = cls.encode_data(obj_t, metadata)
        if not cls.check_encoded(metadata, typedef):
            raise ValueError("Object was not encoded correctly.")
        if not isinstance(data, backwards.bytes_type):
            raise TypeError("Encoded data must be of type %s, not %s" % (
                            backwards.bytes_type, type(data)))
        return metadata, data

    @classmethod
    def decode(cls, metadata, data, typedef=None):
        r"""Decode an object.

        Args:
            metadata (dict): Meta data describing the data.
            data (bytes): Encoded data.
            typedef (dict, optional): Type properties that decoded object should
                be tested against. Defaults to None and object may have any
                values for the type properties (so long as they match the schema).

        Returns:
            object: Decoded object.

        Raises:
            ValueError: If the metadata does not match the type definition.
            ValueError: If the decoded object does not match type definition.

        """
        if not cls.check_encoded(metadata, typedef):
            raise ValueError("Metadata does not match type definition.")
        out = cls.decode_data(data, metadata)
        if not cls.check_decoded(out, typedef):
            raise ValueError("Object was not decoded correctly.")
        out = cls.transform_type(out, typedef)
        return out

    def serialize(self, obj, **kwargs):
        r"""Serialize a message.

        Args:
            obj (object): Python object to be formatted.

        Returns:
            bytes, str: Serialized message.

        """
        metadata, data = self.__class__.encode(obj, self._typedef)
        metadata.update(**kwargs)
        msg = backwards.unicode2bytes(json.dumps(metadata, sort_keys=True))
        msg += self.sep
        msg += data
        return msg
    
    def deserialize(self, msg):
        r"""Deserialize a message.

        Args:
            msg (str, bytes): Message to be deserialized.

        Returns:
            tuple(obj, dict): Deserialized message and header information.

        Raises:
            TypeError: If msg is not bytes type (str on Python 2).
            ValueError: If msg does not contain the header separator.

        """
        if not isinstance(msg, backwards.bytes_type):
            raise TypeError("Message to be deserialized is not bytes type.")
        if len(msg) == 0:
            obj = self._empty_msg
            metadata = dict()
        else:
            if self.sep not in msg:
                raise ValueError("Separator '%s' not in message." % self.sep)
            metadata, data = msg.split(self.sep, 1)
            metadata = json.loads(backwards.bytes2unicode(metadata))
            obj = self.__class__.decode(metadata, data, self._typedef)
        return obj, metadata
