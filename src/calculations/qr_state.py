"""
This class represents a state which all QR functions should (in the future - TODO)
depend upon to do any QR operation - whether passing an instance of the QR state
into a function, or calling a method, or setting the active QR state is not for
us to decide. To reiterate, this class does NOT contain any functionality of its
own - it should merely be a place for common QR variables, etc., to reside."""

from utils import read_schema

"""
In case we need to use this string more than once"""
QR_SCHEMA_PATH = 'schema/match_collection_qr_schema.yml'

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
