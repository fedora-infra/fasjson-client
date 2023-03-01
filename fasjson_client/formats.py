from bravado_core.formatter import SwaggerFormat, NO_OP

mask_format = SwaggerFormat(
    # name of the format as used in the Swagger spec
    format="mask",
    description="Fields list to return.",
    # Callable to convert the field list to a string
    to_wire=lambda fields: ",".join(fields) if isinstance(fields, list) else fields,
    # Callable to convert a string to a field list
    to_python=lambda fields_string: fields_string.split(","),
    # No validation
    validate=NO_OP,
)
