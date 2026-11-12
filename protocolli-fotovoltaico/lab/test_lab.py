"""Test del laboratorio:  python3 -m unittest -v test_lab.py"""

import struct
import threading
import time
import unittest

import iec104
import mbtcp
import modbus_rtu
import sunspec
from sim_inverter import SunSpecInverter, make_server


class TestFrames(unittest.TestCase):
    def test_crc_esempio_classico(self):
        frame = modbus_rtu.build_rtu(1, struct.pack(">BHH", 3, 0, 10))
        self.assertEqual(frame.hex(" ").upper(), "01 03 00 00 00 0A C5 CD")
        self.assertTrue(modbus_rtu.check_rtu(frame))

    def test_gateway_tcp_rtu(self):
        pdu = struct.pack(">BHH", 3, 40072, 50)
        rtu = modbus_rtu.tcp_to_rtu(mbtcp.build_adu(9, 4, pdu))
        self.assertEqual(rtu[0], 4)
        self.assertEqual(rtu[1:-2], pdu)
        self.assertTrue(modbus_rtu.check_rtu(rtu))

    def test_iec104_misura(self):
        frame = iec104.i_frame(3, 7, iec104.float_measure(1, 1001, 1234.5))
        text = "\n".join(iec104.decode(frame))
        self.assertIn("N(S)=3 N(R)=7", text)
        self.assertIn("IOA=1001", text)
        self.assertIn("1234.500", text)

    def test_signed_e_scale_factor(self):
        self.assertEqual(sunspec.to_signed16(0xFFFE), -2)
        regs = [0] * 50
        off = sunspec.point_offsets(sunspec.MODEL_103)
        regs[off["W"]] = 1234
        regs[off["W_SF"]] = (-1) & 0xFFFF
        regs[off["TmpSnk"]] = 0x8000
        data = sunspec.decode_model(103, regs)
        self.assertEqual(data["W"][0], 123.4)
        self.assertIsNone(data["TmpSnk"][0])


class TestSimulatore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inverter = SunSpecInverter(unit_id=1, wmax=20000)
        cls.server = make_server(cls.inverter, "127.0.0.1", 0)   # porta 0 = scelta dal sistema
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def client(self, unit=1):
        return mbtcp.ModbusTcpClient("127.0.0.1", self.port, unit).connect()

    def test_discovery(self):
        with self.client() as c:
            base, models = sunspec.discover(c)
            self.assertEqual(base, 40000)
            self.assertEqual([(m, l) for m, _s, l in models], [(1, 66), (103, 50), (123, 24)])
            self.assertEqual(sunspec.read_model(c, models, 1)["Mn"][0], "LabSolar")

    def test_limitazione_e_watchdog(self):
        with self.client() as c:
            _b, models = sunspec.discover(c)
            sunspec.set_power_limit(c, models, 25, revert_s=1)
            inv = sunspec.read_model(c, models, 103)
            self.assertLessEqual(inv["W"][0], 5000)
            self.assertEqual(inv["St"][0], 5)                        # THROTTLED
            time.sleep(1.3)
            ctl = sunspec.read_model(c, models, 123)
            self.assertEqual(ctl["WMaxLim_Ena"][0], 0)                # il limite e' decaduto
            self.assertGreater(sunspec.read_model(c, models, 103)["W"][0], 5000)

    def test_eccezioni(self):
        with self.client() as c:
            with self.assertRaises(mbtcp.ModbusException) as ctx:
                c.read_holding_registers(30000, 2)
            self.assertEqual(ctx.exception.code, 0x02)               # indirizzo illegale
            with self.assertRaises(mbtcp.ModbusException) as ctx:
                c.write_single_register(40072, 0)                     # registro di sola lettura
            self.assertEqual(ctx.exception.code, 0x02)
            _b, models = sunspec.discover(c)
            with self.assertRaises(mbtcp.ModbusException) as ctx:
                sunspec.set_power_limit(c, models, 150)               # 150% non ha senso
            self.assertEqual(ctx.exception.code, 0x03)
        with self.client(unit=7) as c:
            with self.assertRaises(mbtcp.ModbusException) as ctx:
                c.read_holding_registers(40000, 2)
            self.assertEqual(ctx.exception.code, 0x0B)               # slave inesistente


if __name__ == "__main__":
    unittest.main()
