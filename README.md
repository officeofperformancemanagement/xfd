# xfd
Unofficial Reader of [Extended File Descriptors](https://www.microfocus.com/documentation/extend-acucobol/925/BKUSUSFILES017.html)

## install
```sh
pip install xfd
```

## usage
```py
import xfd

with open("data.xfd") as f:
    text = f.read()

xfd.read(text)
{
    "Identification Section": {
        "select-name": "PIZZAORDERS",
        "table-name": "PIZZAORDERS",
        "file-organization": "Indexed",
        "maximum-record-size": 248,
        "minimum-record-size": 248,
        "number-of-keys": 8,
        "sign-compatability": 0,
        "maximum-numeric-digits": 18,
        "period-character": ".",
        "comma-character": ",",
        "alphabet": "ASCII"
    },
    "Field Section": {
        "summary": {
            "elementary-items": 10,
            "elementary-items-with-occurs": 10,
            "total-items": 13,
            "total-items-with-occurs": 13
        },
        "fields": [
            {
                "field-offset": 0,
                "field-bytes": 112,
                "field-type": 16,
                "field-type-description": "Alphanumeric",
                "field-length": 112,
                "field-scale": 0,
                "field-user-flags": 0,
                "field-user-type": "no user type",
                "field-condition": 999,
                "field-condition-description": "field is technically a group item, which is a collection of multiple fields",
                "field-level": 1,
                "field-name": "PIZZA-REC"
            },
            {
                "field-offset": 0,
                "field-bytes": 2,
                "field-type": 16,
                "field-type-description": "Alphanumeric",
                "field-length": 2,
                "field-scale": 0,
                "field-user-flags": 0,
                "field-user-type": "no user type",
                "field-condition": 0,
                "field-condition-description": "field is in all the records",
                "field-level": 5,
                "field-name": "PIZZA-TYPE"
            },
            # ...
        ]
    }
}
```

## references
- https://www.microfocus.com/documentation/extend-acucobol/925/BKUSUSFILEUS5.3.4.html
