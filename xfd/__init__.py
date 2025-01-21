field_types = dict([
    (0, "Numeric edited"),
    (1, "Unsigned numeric"),
    (2, "Signed numeric (trailing separate)"),
    (3, "Signed numeric (training combined)"),
    (4, "Signed numeric (leading separate)"),
    (5, "Signed numeric (leading combined)"),
    (6, "Signed computational"),
    (7, "Unsigned computational"),
    (8, "Positive packed-decimal"),
    (9, "Signed packed-decimal"),
    (10, "Computational-6"),
    (11, "Signed binary"),
    (12, "Unsigned binary"),
    (13, "Signed native-order binary"),
    (14, "Unsigned native-order binary"),
    # 15 skipped
    (16, "Alphanumeric"),
    (17, "Alphanumeric (justified)"),
    (18, "Alphabetic"),
    (19, "Alphabetic (justified)"),
    (20, "Alphanumeric edited"),
    # 21 skipped
    (22, "Group"),
    (23, "Float or double"),
    (24, "National"),
    (25, "National (justified)"),
    (26, "National edited"),
    (27, "Wide"),
    (28, "Wide (justified)"),
    (29, "Wide edited")
])

field_user_types = dict([
    (0, "no user type"),
    (1, "date fields"),
    (2, "binary fields"),
    (3, "variable-length character")
])

field_condition_description = dict([
    (0, "field is in all the records"),
    (999, "field is technically a group item, which is a collection of multiple fields")
])

file_organization_description = dict([
    (12, "Indexed"),
    (8, "Relative"),
    (4, "Sequential")
])

character_lookup = dict([
    (44, ','),
    (46, ".")
])

alphabet_lookup = dict([
    (0, "ASCII")
])

def identification_xml(
    select_name,
    table_name,
    maximum_record_size,
    minimum_record_size,
    number_of_keys,
    sign_compatability,
    maximum_numeric_digits,
    period_character=".",
    comma_character=",",
    alphabet="ASCII"
):
    return f'''<xfd:identification xfd:version="6">
  <xfd:select-name>{select_name}</xfd:select-name>
  <xfd:table-name>{table_name}</xfd:table-name>
  <xfd:file-organization>Indexed</xfd:file-organization>
  <xfd:maximum-record-size>{maximum_record_size}</xfd:maximum-record-size>
  <xfd:minimum-record-size>{minimum_record_size}xfd:minimum-record-size>
  <xfd:number-of-keys>{number_of_keys}</xfd:number-of-keys>
  <xfd:sign-compatibility>{sign_compatability}</xfd:sign-compatibility>
  <xfd:maximum-numeric-digits>{maximum_numeric_digits}</xfd:maximum-numeric-digits>
  <xfd:period-character>{period_character}</xfd:period-character>
  <xfd:comma-character>{comma_character}</xfd:comma-character>
  <xfd:alphabet>{alphabet}</xfd:alphabet>
</xfd:identification>'''     

def parse_identification_section(text):
    lines = text.strip().split("\n")
    if len(lines) != 4: raise Exception("unexpected length of identification section")
    _, xfd_version, select_name, table_name, file_organization = lines[1].split(",")
    maximum_record_size, minimum_record_size, number_of_keys = lines[2].split(",")
    sign_compatability,maximum_numeric_digits,period_character,comma_character,alphabet = lines[3].split(",")
    return {
        "select-name": select_name,
        "table-name": table_name,
        "file-organization": file_organization_description[int(file_organization)],
        "maximum-record-size": int(maximum_record_size),
        "minimum-record-size": int(minimum_record_size),
        "number-of-keys": int(number_of_keys),
        "sign-compatability": int(sign_compatability),
        "maximum-numeric-digits": int(maximum_numeric_digits),
        "period-character": character_lookup[int(period_character)],
        "comma-character": character_lookup[int(comma_character)],
        "alphabet": alphabet_lookup[int(alphabet)]
    }

def parse_fields_text(text):
    header, summary, *rest = text.strip().split("\n")
    elementary_items, elementary_items_with_occurs, total_items, total_items_with_occurs = summary.split(",")
    fields = []
    for line in rest:
        field_offset, field_bytes, field_type, field_length, field_scale, field_user_flags, field_condition, field_level, field_name = line.split(",")
        fields.append({
            "field-offset": int(field_offset),
            "field-bytes": int(field_bytes),
            "field-type": int(field_type),
            "field-type-description": field_types[int(field_type)],
            "field-length": int(field_length),
            "field-scale": int(field_scale),
            "field-user-flags": int(field_user_flags),
            "field-user-type": field_user_types[int(field_user_flags)],
            "field-condition": int(field_condition),
            "field-condition-description": field_condition_description[int(field_condition)],
            "field-level": int(field_level),
            "field-name": field_name
        })
    return {
        "summary": {
            "elementary-items": int(elementary_items),
            "elementary-items-with-occurs": int(elementary_items_with_occurs),
            "total-items": int(total_items),
            "total-items-with-occurs": int(total_items_with_occurs)
        },
        "fields": fields
    }
        

def parse_key_section(text):
    pass

def parse_text(xfd):
    # split sections
    sections = xfd.split("#")

    # trim sections
    sections = [it.strip() for it in sections]

    # filter out comments
    sections = [section for section in sections if not section.startswith("Generated") and not ("generated by " in section)]

    id_text = next(it for it in sections if it.startswith("[Identification Section]"))
    id_data = parse_identification_section(id_text)

    field_section_text = next(it for it in sections if it.startswith("[Field Section]"))
    field_section_data = parse_fields_text(field_section_text)

    return {
        "Identification Section": id_data,
        "Field Section": field_section_data
    }
