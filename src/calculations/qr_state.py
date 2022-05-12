"""
This class represents a state which all QR functions should (in the future - TODO)
depend upon to do any QR operation - whether passing an instance of the QR state
into a function, or calling a method, or setting the active QR state is not for
us to decide. To reiterate, this class does NOT contain any functionality of its
own - it should merely be a place for common QR variables, etc., to reside."""

import utils

SCHEMA = utils.read_schema("schema/match_collection_qr_schema.yml")

"""
In case we need to use this string more than once"""
QR_SCHEMA_PATH = "schema/match_collection_qr_schema.yml"

"""
An instance of this class represents a state for all QR operations. So this stores
QR-related variables, e.g. internal schema representations."""


class QRState:

    qr_schema: dict

    """
    No arguments are needed right now - this just reads a preset file into the
    schema dictionary."""

    def __init__(self):
        self.qr_schema = utils.read_schema(QR_SCHEMA_PATH)

    @staticmethod
    def _get_data_fields(section):
        """Get data fields of a section in the schema.

        Filters out all entries beginning with '_' as they contain information about the
        (de)compression process, not what data fields should be present.
        """
        data_fields = set()
        for field in SCHEMA[section]:
            # Filter out '_' at start of entry
            if not field.startswith("_"):
                data_fields.add(field)
        return data_fields

    @staticmethod
    def get_timeline_info():
        """Loads information about timeline fields."""
        timeline_fields = []
        for field, field_list in SCHEMA["timeline"].items():
            field_data = {
                "name": field,
                "length": field_list[0],
                "type": field_list[1],
                "position": field_list[2],
            }
            timeline_fields.append(field_data)
        # Sort timeline_fields by the position they appear in
        timeline_fields.sort(key=lambda x: x["position"])
        return timeline_fields
