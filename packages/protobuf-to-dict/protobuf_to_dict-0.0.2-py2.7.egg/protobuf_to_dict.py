from google.protobuf.descriptor import FieldDescriptor


__all__ = ["protobuf_to_dict", "TYPE_CALLABLE_MAP"]


TYPE_CALLABLE_MAP = {
    FieldDescriptor.TYPE_DOUBLE: float,
    FieldDescriptor.TYPE_FLOAT: float,
    FieldDescriptor.TYPE_INT32: int,
    FieldDescriptor.TYPE_INT64: long,
    FieldDescriptor.TYPE_UINT32: int,
    FieldDescriptor.TYPE_UINT64: long,
    FieldDescriptor.TYPE_SINT32: int,
    FieldDescriptor.TYPE_SINT64: long,
    FieldDescriptor.TYPE_FIXED32: int,
    FieldDescriptor.TYPE_FIXED64: long,
    FieldDescriptor.TYPE_SFIXED32: int,
    FieldDescriptor.TYPE_SFIXED64: long,
    FieldDescriptor.TYPE_BOOL: bool,
    FieldDescriptor.TYPE_STRING: unicode,
    FieldDescriptor.TYPE_BYTES: lambda b: b.encode("base64"),
    FieldDescriptor.TYPE_ENUM: int,
}


def repeated(type_callable):
    return lambda value_list: [type_callable(value) for value in value_list]


def protobuf_to_dict(pb, type_callable_map=TYPE_CALLABLE_MAP):
    result_dict = {}
    for field, value in pb.ListFields():
        if field.type not in type_callable_map:
            raise TypeError("Field %s.%s has unrecognised type id %d" % (
                pb.__class__.__name__, field.name, field.type))
        type_callable = type_callable_map[field.type]
        if field.label == FieldDescriptor.LABEL_REPEATED:
            type_callable = repeated(type_callable)
        result_dict[field.name] = type_callable(value)
    return result_dict


# recursion, bitches.
TYPE_CALLABLE_MAP[FieldDescriptor.TYPE_MESSAGE] = protobuf_to_dict
