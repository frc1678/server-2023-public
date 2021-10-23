import insert_fake_data
import server
from calculations import decompressor

DECOMPRESSOR = decompressor.Decompressor(server.Server())


def test_fake_name():
    assert isinstance(insert_fake_data.fake_name(), str)


def test_insert_fake_qr_data():
    # Use decompressor function to check if qrs match schema
    formatted_fake_qrs = []
    for qr in insert_fake_data.insert_fake_qr_data():
        formatted_fake_qrs.append({'data': qr})

    DECOMPRESSOR.decompress_qrs(formatted_fake_qrs)


def test_insert_fake_non_qr_data():
    assert len(insert_fake_data.insert_fake_non_qr_data()[0]) == len(insert_fake_data.TEAMS)
    assert len(insert_fake_data.insert_fake_non_qr_data()[1]) == len(insert_fake_data.TEAMS)
    for obj_data in insert_fake_data.insert_fake_non_qr_data()[0]:
        assert obj_data['team_number'] in insert_fake_data.TEAMS
    for subj_data in insert_fake_data.insert_fake_non_qr_data()[1]:
        assert subj_data['team_number'] in insert_fake_data.TEAMS
