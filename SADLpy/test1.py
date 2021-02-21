import SADL
import Compression.Procyon as pro

sadl = SADL.SADL("tests/ST_001.SAD", 0, True)

sadl.initialize()
sadl.save_wav("TEST1.wav", False)

sadl.import_("TEST1.wav")
encoded = sadl.encode_with_encoding(SADL.Coding.NDS_PROCYON)
sadl.write_file("TEST2.SAD", encoded)

sadl = SADL.SADL("TEST2.SAD", 0, True)
sadl.initialize()
sadl.save_wav("TEST2.wav", False)
