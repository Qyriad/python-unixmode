from unixmode import PureMode

def test_raw_roundtrip():
    sysdir = PureMode.SYSTEM_DIR
    sysdir_raw = sysdir.to_raw()
    sysdir_roundtrip = PureMode.from_raw(sysdir_raw)
    assert sysdir == sysdir_roundtrip
    assert sysdir_raw == sysdir_roundtrip.to_raw()
