#!/usr/bin/env python3
# Copyright (c) 2020 FRC Team 1678: Citrus Circuits
"""Implements server side compressed

This is used to allow QR codes to be modified and fake data to be generated for system tests.
"""

from calculations.qr_state import QRState
import utils


SCHEMA = utils.read_schema('schema/match_collection_qr_schema.yml')


def compress_timeline(timeline_data):
    """Compresses timeline into string representation"""
    compressed_actions = []
    for entry in timeline_data:
        action_components = []
        for field in QRState.get_timeline_info():
            if field['name'] == 'action_type':
                # Add compressed action representation to action components
                action_components.append(SCHEMA['action_type'][entry['action_type']])
            else:
                value = str(entry[field['name']])
                # Pad left of value with zeroes to length defined in schema
                value = value.rjust(field['length'], '0')
                action_components.append(value)
        compressed_actions.extend(action_components)
    return ''.join(compressed_actions)


def compress_list(section, data):
    """Compresses a list given the section of schema"""
    string_data = (str(x) for x in data)
    return SCHEMA[section]['_separator_internal'].join(string_data)


def compress_section(data, section):
    """Compress any section from the QR schema"""
    compressed_points = []
    # Schema version is required to be at the start and exists for every version
    if section == 'generic_data' and 'schema_version' not in data:
        compressed_points.append(f'A{SCHEMA["schema_file"]["version"]}')
    # TODO Handle bools (not needed currently because no bools)
    for key, value in data.items():
        compressed_key = SCHEMA[section][key][0]
        if key == 'timeline':
            compressed_value = compressed_key + compress_timeline(value)
        elif SCHEMA[section][key][1] == 'list':
            compressed_value = compressed_key + compress_list(section, value)
        else:
            compressed_value = f'{compressed_key}{str(value).upper()}'
        if key == 'schema_version':
            compressed_points.insert(0, compressed_value)
        else:
            compressed_points.append(compressed_value)
    return SCHEMA[section]['_separator'].join(compressed_points)


def compress_obj_tim(tim_data):
    """Compresses a tim into QR string representation."""
    generic_points = {}
    obj_points = {}
    for name, data in tim_data.items():
        if name in SCHEMA['generic_data']:
            generic_points.update({name: data})
        elif name in SCHEMA['objective_tim']:
            obj_points.update({name: data})
    # Compress Generic Data
    compressed_generic = compress_section(generic_points, 'generic_data')
    # Compress Objective Data
    compressed_obj = compress_section(obj_points, 'objective_tim')
    compressed_qr = SCHEMA['generic_data']['_section_separator'].join(
        [compressed_generic, compressed_obj]
    )
    return f'{SCHEMA["objective_tim"]["_start_character"]}{compressed_qr}'


def compress_subj_aim(aim_data):
    """Compresses subjective QRs"""
    generic_points = {}
    subj_points = {}
    for name, data in aim_data.items():
        if name in SCHEMA['generic_data']:
            generic_points.update({name: data})
        elif name in SCHEMA['subjective_aim']:
            subj_points.update({name: data})
    # Compress Generic Data
    compressed_generic = compress_section(generic_points, 'generic_data')
    compressed_subj = compress_section(subj_points, 'subjective_aim')
    compressed_qr = SCHEMA['generic_data']['_section_separator'].join(
        [compressed_generic, compressed_subj]
    )
    return f'{SCHEMA["subjective_aim"]["_start_character"]}{compressed_qr}'
