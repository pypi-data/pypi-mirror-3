# Copyright 2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""JSON serialisation."""

__metaclass__ = type
__all__ = [
    "custom_type_decoder",
    "CustomTypeEncoder",
    "register_serialisable_type",
    ]

import json
from lazr.enum import (
    BaseItem,
    EnumJSONEncoder,
    EnumJSONDecoder,
    )


# The supported types which can be JSON serialised.
# The dict values are 3-tuples of: (class, encoder, decoder).
# 'encoder' and 'decoder' are optional. If not specified, serialisation
# simply exports the object's __dict__.
#
# We specify the out-of-the-box supported object types, but the user can add
# their own by calling register_serialisable_type.
_SERIALISABLE_TYPES = {
    # lazr.enum.DBItem, lazr.enum.Item instances
    "BaseItem": (BaseItem, EnumJSONEncoder, EnumJSONDecoder),
    }


def register_serialisable_type(type_name, class_, encoder=None,
                               decoder=None):
    """Register support for handling a new type of object."""
    _SERIALISABLE_TYPES[type_name] = (class_, encoder, decoder)


class CustomTypeEncoder(json.JSONEncoder):
    """A custom JSONEncoder class that knows how to encode custom objects.

    Custom objects are encoded as JSON object literals with a single key,
    'type_name,full_classname' where:
        type_name is the name key taken from _SERIALISATION_TYPES
        full_classname is the classname of the object being serialised

    The literal value the key maps to depends on whether a json encoder for the
    custom object has been specified. If no object specific encoder is
    specified, the __dict__ of the object encoded is used. If an object
    specific encoder has been specified, the encoded value is used.

    This implementation works recursively in that each value in the __dict__
    of the encoded object is also encoded if it is an instance of one of the
    supported types.

    Usage: json.dumps(some_object, cls=CustomTypeDecoder)
    """

    def default(self, obj):
        for type_name, class_info in _SERIALISABLE_TYPES.items():
            obj_type = class_info[0]
            encoder = None
            if len(class_info) > 1:
                encoder = class_info[1]
            if isinstance(obj, obj_type):
                key = ('%s,%s.%s'
                       % (type_name, obj.__module__, obj.__class__.__name__))
                if encoder is None:
                    encoded_value = obj.__dict__
                else:
                    encoded_value = encoder().encode(obj)
                return { key: encoded_value }
        return json.JSONEncoder.default(self, obj)


def _import(full_classname):
    # A helper method to resolve a classname into a class.
    # Return None if no class can be found.
    components = full_classname.split('.')
    try:
        mod = __import__(components[0])
        for comp in components[1:]:
            if not comp.startswith('_'):
                mod = getattr(mod, comp)
        return mod
    except (ImportError, AttributeError):
        return  None


def custom_type_decoder(json_dict):
    """A JSON loads object_hook which can deserialise complex objects.

    The objects which can be deserialised have been serialised with
    CustomTypeEncoder. If a decoder is available for a class, the from_dict
    method of the decoder is called. If no decoder is available, the object
    class is inspected to see if it provides a from_dict method. Otherwise,
    the dict itself is returned.

    Usage: json.loads(encoded_string, object_hook=custom_type_decoder)
    """
    if len(json_dict) == 1:
        # Determine the type_name and classname.
        classname_info, json_value = json_dict.items()[0]
        type_name, specific_obj_classname = classname_info.split(',')
        # If no registered decoder, return the raw value.
        class_info = _SERIALISABLE_TYPES.get(type_name)
        if not class_info:
            return json_value
        # Attempt to import the object's specific class.
        specific_obj_class = _import(specific_obj_classname)
        if specific_obj_class is None:
            # If not possible, default to the class in the serialisation type
            # map. This is fallback is required to allow doc tests to work.
            obj_class = class_info[0]
        else:
            obj_class = specific_obj_class
        # Decode the dict of object state.
        value_dict = json.loads(
            json_value, object_hook=custom_type_decoder)
        # Deserialise using a decoder if specified or a from_dict() on the
        # object class itself.
        if class_info[2]:
            return class_info[2].from_dict(obj_class, value_dict)
        else:
            class_from_dict = getattr(obj_class, 'from_dict', None)
            if class_from_dict:
                return class_from_dict(value_dict)
            return json_value
    return json_dict
