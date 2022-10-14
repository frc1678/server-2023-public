"""This file houses a calculation class that allows the server to input data"""
from data_transfer import adb_communicator
import calculations.base_calculations
import utils

import datetime

import termcolor


class QRInput(calculations.base_calculations.BaseCalculations):
    def __init__(self, server):
        super().__init__(server)
        self.schema = utils.read_schema("schema/match_collection_qr_schema.yml")

    def upload_qr_codes(self, qr_codes):
        # Acquires current qr data
        qr_data = [qr_code["data"] for qr_code in self.server.db.find("raw_qr")]
        qr = set()

        for qr_code in qr_codes:
            # Check for duplicate QR codes
            if qr_code in qr_data:
                termcolor.cprint(f"WARNING: duplicate QR code not uploaded\t{qr_code}", color="red")
                continue
            # Checks to make sure the qr is valid by checking its starting character
            elif qr_code.startswith(
                self.schema["subjective_aim"]["_start_character"]
            ) or qr_code.startswith(self.schema["objective_tim"]["_start_character"]):
                qr.add(qr_code)
            else:
                utils.log_warning(f'Invalid QR code not uploaded: "{qr_code}"')
        if qr != set():
            curr_time = datetime.datetime.now()
            qr = [
                {
                    "data": qr_code,
                    "blocklisted": False,
                    "epoch_time": curr_time.timestamp(),
                    "readable_time": curr_time.strftime("%D - %H:%M:%S"),
                }
                for qr_code in qr
            ]
            self.server.db.insert_documents("raw_qr", qr)

    def run(self):
        # Grabs QR codes from user, strips whitespace, split by tab
        qr_codes = input(termcolor.colored("ENTER DATA: ", "green"))
        if qr_codes != "":
            self.upload_qr_codes(qr_codes.strip().split("\t"))
        adb_communicator.pull_device_data()
