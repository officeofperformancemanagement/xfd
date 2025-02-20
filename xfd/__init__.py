from bs4 import BeautifulSoup

field_types = dict(
    [
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
        (12, "Unsigned binare-order binary"),
        (14, "Unsigned naty"),
        (13, "Signed nativive-order binary"),
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
        (29, "Wide edited"),
    ]
)

field_user_types = dict(
    [
        (0, "no user type"),
        (1, "date field"),
        (2, "binary field"),
        (3, "variable-length character"),
    ]
)

field_condition_description = dict(
    [
        (0, "field is in all the records"),
        (
            999,
            "field is technically a group item, which is a collection of multiple fields",
        ),
    ]
)

file_organization_description = dict(
    [(12, "Indexed"), (8, "Relative"), (4, "Sequential")]
)

character_lookup = dict([(44, ","), (46, ".")])

alphabet_lookup = dict([(0, "ASCII")])


def identification_xml(
    select_name: str,
    table_name: str,
    maximum_record_size: float,
    minimum_record_size: float,
    number_of_keys: float,
    sign_compatability: float,
    maximum_numeric_digits: float,
    period_character: str = ".",
    comma_character: str = ",",
    alphabet: str = "ASCII",
) -> str:
    return f"""<xfd:identification xfd:version="6">
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
</xfd:identification>"""


def parse_identification_section(text: str) -> dict:
    lines = text.strip().split("\n")
    _, xfd_version, select_name, table_name, file_organization = lines[1].split(",")

    xfd_version = int(xfd_version)

    if len(lines) not in [3, 4]:
        raise Exception("unexpected length of identification section")
    maximum_record_size, minimum_record_size, number_of_keys = lines[2].split(",")

    if xfd_version == 6:
        (
            sign_compatability,
            maximum_numeric_digits,
            period_character,
            comma_character,
            alphabet,
        ) = lines[3].split(",")
    elif xfd_version == 5:
        (
            sign_compatability,
            maximum_numeric_digits,
            period_character,
            comma_character,
            alphabet,
        ) = ["1", maximum_record_size, ord("."), ord(","), "0"]

    return {
        "version": xfd_version,
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
        "alphabet": alphabet_lookup[int(alphabet)],
    }


def parse_fields_text(text: str) -> dict:
    header, summary, *rest = text.strip().split("\n")
    (
        elementary_items,
        elementary_items_with_occurs,
        total_items,
        total_items_with_occurs,
    ) = summary.split(",")
    fields = []
    for line in rest:
        if "START-OCCURS" in line:
            raise Exception("START-OCCURS in fields not supported")
        (
            field_offset,
            field_bytes,
            field_type,
            field_length,
            field_scale,
            field_user_flags,
            field_condition,
            field_level,
            field_name,
        ) = line.split(",")
        field_user_flags = int(field_user_flags)
        fields.append(
            {
                "field-offset": int(field_offset),
                "field-bytes": int(field_bytes),
                "field-type": int(field_type),
                "field-type-description": field_types[int(field_type)],
                "field-length": int(field_length),
                "field-scale": int(field_scale),
                "field-user-flags": field_user_flags,
                "field-user-type": field_user_types[field_user_flags % 16],
                "field-user-type-table": "secondary"
                if field_user_flags >= 16
                else "primary",
                "field-condition": int(field_condition),
                "field-condition-description": field_condition_description[
                    int(field_condition)
                ],
                "field-level": int(field_level),
                "field-name": field_name,
            }
        )
    return {
        "summary": {
            "elementary-items": int(elementary_items),
            "elementary-items-with-occurs": int(elementary_items_with_occurs),
            "total-items": int(total_items),
            "total-items-with-occurs": int(total_items_with_occurs),
        },
        "fields": fields,
    }


def parse_key_section(text: str):
    pass


def parse_text(xfd: str) -> dict:
    # split sections
    sections = xfd.split("#")

    # trim sections
    sections = [it.strip() for it in sections]

    # filter out comments
    sections = [
        section
        for section in sections
        if not section.startswith("Generated") and not ("generated by " in section)
    ]

    id_text = next(it for it in sections if it.startswith("[Identification Section]"))
    id_data = parse_identification_section(id_text)

    field_section_text = next(it for it in sections if it.startswith("[Field Section]"))
    field_section_data = parse_fields_text(field_section_text)

    return {"Identification Section": id_data, "Field Section": field_section_data}


def parse_xml(xmltext: str) -> dict:
    soup = BeautifulSoup(xmltext, features="lxml")
    xid = soup.find("xfd:identification")

    results = {}

    version = int(xid["xfd:version"])

    if version == 5:
        results["Identification Section"] = {
            "select-name": xid.find("xfd:select-name").text,
            "table-name": xid.find("xfd:table-name").text,
            "file-organization": xid.find("xfd:file-organization").text,
            "maximum-record-size": int(xid.find("xfd:maximum-record-size").text),
            "minimum-record-size": int(xid.find("xfd:minimum-record-size").text),
            "number-of-keys": int(xid.find("xfd:number-of-keys").text),
            "sign-compatability": None,
            "maximum-numeric-digits": None,
            "period-character": ".",
            "comma-character": ",",
            "alphabet": "ASCII",
        }
    elif version == 6:
        results["Identification Section"] = {
            "select-name": xid.find("xfd:select-name").text,
            "table-name": xid.find("xfd:table-name").text,
            "file-organization": xid.find("xfd:file-organization").text,
            "maximum-record-size": int(xid.find("xfd:maximum-record-size").text),
            "minimum-record-size": int(xid.find("xfd:minimum-record-size").text),
            "number-of-keys": int(xid.find("xfd:number-of-keys").text),
            "sign-compatability": int(xid.find("xfd:sign-compatibility").text),
            "maximum-numeric-digits": int(xid.find("xfd:maximum-numeric-digits").text),
            "period-character": xid.find("xfd:period-character").text,
            "comma-character": xid.find("xfd:comma-character").text,
            "alphabet": xid.find("xfd:alphabet").text,
        }

    xfs = soup.find("xfd:fields")
    results["Field Section"] = {
        "summary": {
            "elementary-items": int(xfs["xfd:elementary-items"]),
            "elementary-items-with-occurs": int(
                xfs["xfd:elementary-items-with-occurs"]
            ),
            "total-items": int(xfs["xfd:total-items"]),
            "total-items-with-occurs": int(xfs["xfd:total-items-with-occurs"]),
        },
        "fields": [],
    }

    for fld in xfs.find_all("xfd:field"):
        field_type = int(fld["xfd:field-type"])
        field_user_flags = int(fld["xfd:field-user-flags"])
        field_condition = int(fld["xfd:field-condition"])
        results["Field Section"]["fields"].append(
            {
                "field-offset": int(fld["xfd:field-offset"]),
                "field-bytes": int(fld["xfd:field-bytes"]),
                "field-type": field_type,
                "field-type-description": field_types[field_type],
                "field-length": int(fld["xfd:field-length"]),
                "field-scale": int(fld["xfd:field-scale"]),
                "field-user-flags": field_user_flags,
                "field-user-type": field_user_types[field_user_flags % 16],
                "field-user-type-table": "secondary"
                if field_user_flags >= 16
                else "primary",
                "field-condition": field_condition,
                "field-condition-description": field_condition_description[
                    field_condition
                ],
                "field-level": int(fld["xfd:field-level"]),
                "field-name": fld["xfd:field-name"],
            }
        )
    return results


def parse(rawtext: str) -> dict:
    if rawtext.startswith("<?xml"):
        return parse_xml(rawtext)
    else:
        return parse_text(rawtext)
