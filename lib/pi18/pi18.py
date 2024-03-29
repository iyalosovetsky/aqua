COMMANDS = {
    # QUERY #
    "ET": {
        "name": "ET",
        "prefix": "^P005",
        "description": "Total Generated Energy query",
        "help": " -- Query total generated energy",
        "type": "QUERY",
        "response": [["int", "Total generated energy", "Wh"]],
        "test_responses": [
            b"",
        ],
    },
    "EY": {
        "name": "EY",
        "prefix": "^P009",
        "description": "Query generated energy of year",
        "help": " -- queries generated energy for the year YYYY from the Inverter",
        "type": "QUERY",
        "response": [["int", "Year generated energy", "Wh"]],
        "test_responses": [
            b"",
        ],
        "regex": "EY(\\d\\d\\d\\d)$",
    },
    "EM": {
        "name": "EM",
        "prefix": "^P011",
        "description": "Query generated energy of month",
        "help": " -- queries generated energy for the year YYYY and month MM from the Inverter",
        "type": "QUERY",
        "response": [["int", "Month generated energy", "Wh"]],
        "test_responses": [
            b"",
        ],
        "regex": "EM(\\d\\d\\d\\d\\d\\d)$",
    },
    "ED": {
        "name": "ED",
        "prefix": "^P013",
        "description": "Query generated energy of day",
        "help": " -- queries generated energy for the day YYYYMMDD from the Inverter",
        "type": "QUERY",
        "response": [["int", "Day generated energy", "Wh"]],
        "test_responses": [
            b"",
        ],
        "regex": "ED(\\d\\d\\d\\d\\d\\d\\d\\d)$",
    },     
    "ID": {
        "name": "ID",
        "prefix": "^P005",
        "description": "Device Serial Number inquiry",
        "help": " -- queries the device serial number",
        "type": "QUERY",
        "response": [["string", "Serial Number", ""]],
        "test_responses": [
            b"^D02514012345678901234567\r",
        ],
    },
    "VFW": {
        "name": "VFW",
        "prefix": "^P006",
        "description": "Device CPU version inquiry",
        "help": " -- queries the CPU version",
        "type": "QUERY",
        "response": [
            ["int", "Main CPU Version", ""],
            ["int", "Slave 1 CPU Version", ""],
            ["int", "Slave 2 CPU Version", ""],
        ],
        "test_responses": [
            b"^^D02005220,00000,00000\r",
        ],
    },
    "PIRI": {
        "name": "PIRI",
        "prefix": "^P007",
        "description": "Device rated information",
        "help": " -- queries rated information",
        "type": "QUERY",
        "response": [
            ["10int", "AC input rated voltage", "V"],
            ["10int", "AC input rated current", "A"],
            ["10int", "AC output rated voltage", "V"],
            ["10int", "AC output rated frequency", "Hz"],
            ["10int", "AC output rated current", "A"],
            ["int", "AC output rating apparent power", "VA"],
            ["int", "AC output rating active power", "W"],
            ["10int", "Battery rated voltage", "V"],
            ["10int", "Battery re-charge voltage", "V"],
            ["10int", "Battery re-discharge voltage", "V"],
            ["10int", "Battery under voltage", "V"],
            ["10int", "Battery bulk voltage", "V"],
            ["10int", "Battery float voltage", "V"],
            ["option", "Battery type", ["AGM", "Flooded", "User"]],
            ["int", "Max AC charging current", "A"],
            ["int", "Max charging current", "A"],
            ["option", "Input voltage rang", ["Appliance", "UPS"]],
            [
                "option",
                "Output source priority",
                ["Solar-Utility-Battery", "Solar-Battery-Utility"],
            ],
            [
                "option",
                "Charger source priority",
                ["Solar First", "Solar and Utility", "Only Solar"],
            ],
            ["int", "Parallel max num", ""],
            ["option", "Machine type", ["Off-Grid", "Grid-Tie"]],
            ["option", "Topology", ["transformerless", "transformer"]],
            [
                "option",
                "Output model setting",
                [
                    "Single module",
                    "parallel output",
                    "Phase 1 of three phase output",
                    "Phase 2 of three phase output",
                    "Phase 3 of three phase output",
                ],
            ],
            [
                "option",
                "Solar power priority",
                ["Battery-Load-Utiliy + AC Charger", "Load-Battery-Utiliy"],
            ],
            ["int", "MPPT strings", ""],
        ],
        "test_responses": [
            b"^D0882300,217,2300,500,217,5000,5000,480,500,540,450,552,545,2,10,060,1,1,1,9,1,0,0,0,1,00\r",
            b"^D0882300,217,2300,500,217,5000,5000,480,500,540,450,560,560,2,02,060,1,0,1,9,1,0,0,0,1,00\xe9\r",
        ],
    },
    "GS": {
        "name": "GS",
        "prefix": "^P005",
        "description": "General status query",
        "help": " -- Query general status information",
        "type": "QUERY",
        "response": [
            ["10int", "Grid voltage", "V"],
            ["10int", "Grid frequency", "Hz"],
            ["10int", "AC output voltage", "V"],
            ["10int", "AC output frequency", "Hz"],
            ["int", "AC output apparent power", "VA"],
            ["int", "AC output active power", "W"],
            ["int", "Output load percent", "%"],
            ["10int", "Battery voltage", "V"],
            ["10int", "Battery voltage from SCC", "V"],
            ["10int", "Battery voltage from SCC2", "V"],
            ["int", "Battery discharge current", "A"],
            ["int", "Battery charging current", "A"],
            ["int", "Battery capacity", "%"],
            ["int", "Inverter heat sink temperature", "C"],
            ["int", "MPPT1 charger temperature", "C"],
            ["int", "MPPT2 charger temperature", "C"],
            ["int", "PV1 Input power", "W"],
            ["int", "PV2 Input power", "W"],
            ["10int", "PV1 Input voltage", "V"],
            ["10int", "PV2 Input voltage", "V"],
            [
                "option",
                "Setting value configuration state",
                ["Nothing changed", "Something changed"],
            ],
            [
                "option",
                "MPPT1 charger status",
                ["abnormal", "normal but not charged", "charging"],
            ],
            [
                "option",
                "MPPT2 charger status",
                ["abnormal", "normal but not charged", "charging"],
            ],
            ["option", "Load connection", ["disconnect", "connect"]],
            ["option", "Battery power direction", ["donothing", "charge", "discharge"]],
            ["option", "DC/AC power direction", ["donothing", "AC-DC", "DC-AC"]],
            ["option", "Line power direction", ["donothing", "input", "output"]],
            ["int", "Local parallel ID", ""],
        ],
        "test_responses": [
            b"D1062232,499,2232,499,0971,0710,019,008,000,000,000,000,000,044,000,000,0520,0000,1941,0000,0,2,0,1,0,2,1,0\x09\x7b\r",
            b"^0\x1b\xe3\r",
        ],
    },
    "MOD": {
        "name": "MOD",
        "prefix": "^P006",
        "description": "Working mode query",
        "help": " -- Query the working mode",
        "type": "QUERY",
        "response": [
            [
                "option",
                "Working mode",
                [
                    "Power on mode",
                    "Standby mode",
                    "Bypass mode",
                    "Battery mode",
                    "Fault mode",
                    "Hybrid mode(Line mode, Grid mode)",
                ],
            ],
        ],
        "test_responses": [
            b"",
        ],
    },
    #    "FWS": {
    #        "name": "FWS",
    #        "prefix": "^P005",
    #        "description": "fault and warning status",
    #        "help": " -- Query fault and warning status",
    #        "type": "QUERY",
    #        "response": [
    #            [
    #            ]
    #        ],
    #        "test_responses": [
    #            b"",
    #        ],
    #    },
    "FLAG": {
        "name": "FLAG",
        "prefix": "^P007",
        "description": "Query enable/disable flag status",
        "help": " -- queries enable/disable flag status from the Inverter",
        "type": "QUERY",
        "response": [
            ["option", "Buzzer beep", ["Disabled", "Enabled"]],
            ["option", "Overload bypass function", ["Disabled", "Enabled"]],
            ["option", "display back to default page", ["Disabled", "Enabled"]],
            ["option", "Overload restart", ["Disabled", "Enabled"]],
            ["option", "Over temperature restart", ["Disabled", "Enabled"]],
            ["option", "Backlight on", ["Disabled", "Enabled"]],
            ["option", "Alarm primary source interrupt", ["Disabled", "Enabled"]],
            ["option", "Fault code record", ["Disabled", "Enabled"]],
            ["int", "Reserved", ""],
        ],
        "test_responses": [
            b"",
        ],
    },
    #    "DI": {
    #        "name": "DI",
    #        "prefix": "^P005",
    #        "description": "Query default value of changeable paramer",
    #        "help": " -- Query default value of changeable paramer",
    #        "type": "QUERY",
    #        "response": [
    #        ],
    #        "test_responses": [
    #            b"",
    #        ],
    #    },
    "MCHGCR": {
        "name": "MCHGCR",
        "prefix": "^P009",
        "description": "Query Max. charging current selectable value",
        "help": " -- Query Max. charging current selectable value",
        "type": "QUERY",
        "response": [
            ["int", "Max. charging current value 1", "A"],
            ["int", "Max. charging current value 2", "A"],
            ["int", "Max. charging current value 3", "A"],
            ["int", "Max. charging current value 4", "A"],
            ["int", "Max. charging current value 5", "A"],
            ["int", "Max. charging current value 6", "A"],
            ["int", "Max. charging current value 7", "A"],
            ["int", "Max. charging current value 8", "A"],
        ],
        "test_responses": [
            b"^D034010,020,030,040,050,060,070,080\x161\r",
        ],
    },
    "MUCHGCR": {
        "name": "MUCHGCR",
        "prefix": "^P010",
        "description": "Query Max. AC charging current selectable value",
        "help": " -- Query Max. AC charging current selectable value",
        "type": "QUERY",
        "response": [
            ["int", "Max. AC charging current value 1", "A"],
            ["int", "Max. AC charging current value 2", "A"],
            ["int", "Max. AC charging current value 3", "A"],
            ["int", "Max. AC charging current value 4", "A"],
            ["int", "Max. AC charging current value 5", "A"],
            ["int", "Max. AC charging current value 6", "A"],
            ["int", "Max. AC charging current value 7", "A"],
            ["int", "Max. AC charging current value 8", "A"],
            ["int", "Max. AC charging current value 9", "A"],
        ],
        "test_responses": [
            b"",
        ],
    },
    "PI": {
        "name": "PI",
        "prefix": "^P005",
        "description": "Device Protocol Version inquiry",
        "help": " -- queries the device protocol version \n",
        "type": "QUERY",
        "response": [["string", "Protocol Version", ""]],
        "test_responses": [
            b"^D00518;\x03\r",
        ],
    },
    # SETTER ###
    #    "LON": {
    #        "name": "LON",
    #        "prefix": "^S007",
    #        "description": "Set enable/disable machine supply power to the loads",
    #        "help": " -- example: LON1 (0: disable, 1: enable)",
    #        "type": "SETTER",
    #        "response": [
    #            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}],
    #        ],
    #        "test_responses": [
    #            b"^1\x0b\xc2\r",
    #            b"^0\x1b\xe3\r",
    #        ],
    #        "regex": "LON([01])$",
    #    },
    "POP": {
        "name": "POP",
        "prefix": "^S007",
        "description": "Set output souce priority 				(Manual Option 01)",
        "help": " -- example: POP0 		(set Output POP0 [0: Solar-Utility-Batter],  POP1 [1: Solar-Battery-Utility]",
        "type": "SETTER",
        "response": [
            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}],
        ],
        "test_responses": [
            b"^1\x0b\xc2\r",
            b"^0\x1b\xe3\r",
        ],
        "regex": "POP([01])$",
    },
    "PSP": {
        "name": "PSP",
        "prefix": "^S007",
        "description": "Set solar power priority 				(Manual Option 05)",
        "help": " -- example: PSP0 		(set Priority PSP0 [0: Battery-Load-Utiliy (+AC Charge)],  PSP1 [1: Load-Battery-Utiliy]",
        "type": "SETTER",
        "response": [
            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}],
        ],
        "test_responses": [
            b"^1\x0b\xc2\r",
            b"^0\x1b\xe3\r",
        ],
        "regex": "PSP([01])$",
    },
    "PEI": {
        "name": "PEI",
        "prefix": "^S006",
        "description": "Set Machine type,  enable: Grid-Tie 			(Manual Option 09)",
        "help": " -- example: PEI 		(set enable Grid-Tie)",
        "type": "SETTER",
        "response": [
            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}],
        ],
        "test_responses": [
            b"^1\x0b\xc2\r",
            b"^0\x1b\xe3\r",
        ],
    },
    "PDI": {
        "name": "PDI",
        "prefix": "^S006",
        "description": "Set Machine type, disable: Grid-Tie 			(Manual Option 09)",
        "help": " -- example: PDI 		(set disable Grid-Tie)",
        "type": "SETTER",
        "response": [
            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}],
        ],
        "test_responses": [
            b"^1\x0b\xc2\r",
            b"^0\x1b\xe3\r",
        ],
    },
    "PCP": {
        "name": "PCP",
        "prefix": "^S009",
        "description": "Set charging source priority 				(Manual Option 10)",
        "help": " -- example: PCP0,1 		(set unit 0 [0-9] to 0: Solar first, 1: Solar and Utility, 2: Only solar)",
        "type": "SETTER",
        "response": [
            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}],
        ],
        "test_responses": [
            b"^1\x0b\xc2\r",
            b"^0\x1b\xe3\r",
        ],
        "regex": "PCP([0-9],[012])$",
    },
    "MCHGC": {
        "name": "MCHGC",
        "prefix": "^S013",
        "description": "Set Battery Max Charging Current Solar + AC 		(Manual Option 11)",
        "help": " -- example: MCHGC0,030 	(set unit 0 [0-9] to max charging current of  30A [    010 020 030 040 050 060 070 080])",
        "type": "SETTER",
        "response": [
            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}],
        ],
        "test_responses": [
            b"(NAK\x73\x73\r",
            b"(ACK\x39\x20\r",
        ],
        "regex": "MCHGC([0-9],0[1-8]0)$",
    },
    "MUCHGC": {
        "name": "MUCHGC",
        "prefix": "^S014",
        "description": "Set Battery Max AC Charging Current 			(Manual Option 13)",
        "help": " -- example: MUCHGC0,030 	(set unit 0 [0-9] utility charging current to 30A [002 010 020 030 040 050 060 070 080])",
        "type": "SETTER",
        "response": [
            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}]
        ],
        "test_responses": [
            b"",
        ],
        "regex": "MUCHGC([0-9]),(002|0[1-8]0)$",
    },
    "PBT": {
        "name": "PBT",
        "prefix": "^S007",
        "description": "Set Battery Type 					(Manual Option 14)",
        "help": " -- example: PBT0 		(set battery as PBT0 [0: AGM], PBT1 [1: FLOODED], PBT2 [2: USER])",
        "type": "SETTER",
        "response": [
            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}]
        ],
        "test_responses": [
            b"(NAK\x73\x73\r",
            b"(ACK\x39\x20\r",
        ],
        "regex": "PBT([012])$",
    },
    "MCHGV": {
        "name": "MCHGV",
        "prefix": "^S015",
        "description": "Set Battery Bulk,Float charge voltages 		     (Manual Option 17,18)",
        "help": " -- example: MCHGV552,540 	(set Bulk - CV voltage [480~584] in 0.1V xxx, Float voltage [480~584] in 0.1V yyy)",
        "type": "SETTER",
        "response": [
            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}],
        ],
        "test_responses": [
            b"^1\x0b\xc2\r",
            b"^0\x1b\xe3\r",
        ],
        # Regex 480 - 584 Volt
        "regex": "MCHGV(4[8-9][0-9]|5[0-7][0-9]|58[0-5]),(4[8-9][0-9]|5[0-7][0-9]|58[0-4])$",
    },
    "PSDV": {
        "name": "PSDV",
        "prefix": "^S010",
        "description": "Set Battery Cut-off Voltage	 			(Manual Option 19)",
        "help": " -- example: PSDV450 		(set battery cut-off voltage to 45V [400~480V] for 48V unit)",
        "type": "SETTER",
        "response": [
            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}]
        ],
        "test_responses": [
            b"(NAK\x73\x73\r",
            b"(ACK\x39\x20\r",
        ],
        "regex": "PSDV(4[0-7][0-9]|480)$",
    },
    "BUCD": {
        "name": "BUCD",
        "prefix": "^S014",
        "description": "Set Battery Stop dis,charging when Grid is available (Manual Option 20,21)",
        "help": " -- example: BUCD440,480	(set Stop discharge Voltage [440~510] in 0.1V xxx, Stop Charge Voltage [000(Full) or 480~580] in 0.1V yyy)",
        "type": "SETTER",
        "response": [
            ["ack", "Command execution", {"NAK": "Failed", "ACK": "Successful"}]
        ],
        "test_responses": [
            b"(NAK\x73\x73\r",
            b"(ACK\x39\x20\r",
        ],
        "regex": "BUCD((4[4-9]0|5[0-1]0),(000|4[8-9]0|5[0-8]0))$",
    },
}


import re


# from protocol_helpers import crcPI as crc
def crc(data_bytes):
    """
    Calculates CRC for supplied data_bytes
    """
    # assert type(byte_cmd) == bytes
    #log.debug(f"Calculating CRC for {data_bytes}")

    crc = 0
    da = 0
    crc_ta = [
        0x0000,
        0x1021,
        0x2042,
        0x3063,
        0x4084,
        0x50A5,
        0x60C6,
        0x70E7,
        0x8108,
        0x9129,
        0xA14A,
        0xB16B,
        0xC18C,
        0xD1AD,
        0xE1CE,
        0xF1EF,
    ]

    for c in data_bytes:
        #log.debug('Encoding %s', c)
        if type(c) == str:
            c = ord(c)
        da = ((crc >> 8) & 0xFF) >> 4
        crc = (crc << 4) & 0xFFFF

        index = da ^ (c >> 4)
        crc ^= crc_ta[index]

        da = ((crc >> 8) & 0xFF) >> 4
        crc = (crc << 4) & 0xFFFF

        index = da ^ (c & 0x0F)
        crc ^= crc_ta[index]

    crc_low = crc & 0xFF
    crc_high = (crc >> 8) & 0xFF

    if crc_low == 0x28 or crc_low == 0x0D or crc_low == 0x0A:
        crc_low += 1
    if crc_high == 0x28 or crc_high == 0x0D or crc_high == 0x0A:
        crc_high += 1

    crc = crc_high << 8
    crc += crc_low

    #log.debug(f"Generated CRC {crc_high:#04x} {crc_low:#04x} {crc:#06x}")
    return [crc_high, crc_low]

class pi18( ):
    def __str__(self):
        return "PI18 protocol handler"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self._protocol_id = b"PI18"
        self.COMMANDS = COMMANDS
        self.STATUS_COMMANDS = [
            "ET",
            "EY",
            "EM",
            "ED",
            "ID",
            "VFW",
            "PIRI",
            "GS",
            "MOD",
            # "FWS",
            "FLAG",
            # "DI",
            "MCHGCR",
            "MUCHGCR",
            "PI",
        ]
        self.SETTINGS_COMMANDS = [
            "PEI" "PDI" "POP"
            # "PCP",
            "PSP",
            "MCHGV",
            "MUCHGC",
        ]
        self.DEFAULT_COMMAND = "PI"

        
    def list_commands(self):
        # print(f"{'Parameter':<30}\t{'Value':<15} Unit")
        if self._protocol_id is None:
            log.error("Attempted to list commands with no protocol defined")
            return {
                "ERROR": ["Attempted to list commands with no protocol defined", ""]
            }
        result = {}
        result["_command"] = "command help"
        result[
            "_command_description"
        ] = f"List available commands for protocol {str(self._protocol_id, 'utf-8')}"
        for command in self.COMMANDS:
            if "help" in self.COMMANDS[command]:
                info = (
                    self.COMMANDS[command]["description"]
                    + self.COMMANDS[command]["help"]
                )
            else:
                info = self.COMMANDS[command]["description"]
            result[command] = [info, ""]
        return result
    
    def get_command_defn(self, command) -> dict:
        #print(f"Processing command '{command}'")
        if command in self.COMMANDS and "regex" not in self.COMMANDS[command]:
            #print(f"Found command {command} in protocol {self._protocol_id}")
            return self.COMMANDS[command]
        for _command in self.COMMANDS:
            if "regex" in self.COMMANDS[_command] and self.COMMANDS[_command]["regex"]:
                #print(f"Regex commands _command: {_command}")
                _re = re.compile(self.COMMANDS[_command]["regex"])
                match = _re.match(command)
                if match:
                    #print(
                    #    f"Matched: {command} to: {self.COMMANDS[_command]['name']} value: {match.group(1)}"
                    #)
                    self._command_value = match.group(1)
                    return self.COMMANDS[_command]
        print(f"No command_defn found for {command}")
        return None
    

    def get_full_command(self, command) -> bytes:
        """
        Override the default get_full_command as its different for PI18
        """
        #print(f"Using protocol {self._protocol_id} with {len(self.COMMANDS)} commands"        )
        # These need to be set to allow other functions to work`
        self._command = command
        self._command_defn = self.get_command_defn(command)
        # End of required variables setting
        if self._command_defn is None:
            return None

        _cmd = bytes(self._command, "utf-8")
        _type = self._command_defn["type"]

        # data_length = len(_cmd) + 2 + 1
        if _type == "QUERY":
            _prefix = self._command_defn["prefix"]
        elif _type == "SETTER":
            _prefix = self._command_defn["prefix"]
            #
            # _prefix = f"^S{data_length:03}"

        else:
            data_length = len(_cmd) + 2 + 1
            _prefix = f"^P{data_length:03}"

        _pre_cmd = bytes(_prefix, "utf-8") + _cmd

        #print(f"_pre_cmd: {_pre_cmd}")
        # calculate the CRC
        crc_high, crc_low = crc(_pre_cmd)
        # combine byte_cmd, CRC , return
        # PI18 full command "^P005GS\x..\x..\r"
        _crc = bytes([crc_high, crc_low, 13])
        full_command = _pre_cmd + _crc

        #print(f"full command: {full_command}")
        return full_command

    def get_responses(self, response):
        """
        Override the default get_responses as its different for PI18
        """
        responses = response.split(b",")
        if responses[0] == b"^0\x1b\xe3\r":
            # is a reject response
            return ["NAK"]
        elif responses[0] == b"^1\x0b\xc2\r":
            # is a successful acknowledgement response
            return ["ACK"]

        # Drop ^Dxxx from first response
        responses[0] = responses[0][5:]
        # Remove CRC of last response
        responses[-1] = responses[-1][:-3]
        return responses


    def check_response_valid(self, response) -> Tuple[bool, dict]:
        """
        Simplest validity check, CRC checks should be added to individual protocols
        """
        if response is None:
            return False, {"ERROR": ["No response", ""]}
        return True, {}

    def process_response(
        self,
        data_name=None,
        data_type=None,
        data_units=None,
        raw_value=None,
        frame_number=0,
    ):
        template = None
        # Check for a format modifying template
        if ":" in data_type:
            data_type, template = data_type.split(":", 1)
            print(f"Got template {template} for {data_name} {raw_value}")
        print(
            f"Processing data_type: {data_type} for data_name: {data_name}, raw_value {raw_value}"
        )
        if data_type == "loop":
            log.warning("loop not implemented...")
            return data_name, None, data_units
        if data_type == "exclude" or data_type == "discard" or raw_value == "extra":
            # Just ignore these ones
            print(f"Discarding {data_name}:{raw_value}")
            return None, raw_value, data_units
        if data_type == "option":
            try:
                key = int(raw_value)
                r = data_units[key]
            except ValueError:
                r = f"Unable to process to int: {raw_value}"
                return None, r, ""
            except IndexError:
                r = f"Invalid option: {key}"
            return data_name, r, ""
        if data_type == "hex_option":
            key = int(raw_value[0])
            if key < len(data_units):
                r = data_units[key]
            else:
                r = f"Invalid hex_option: {key}"
            return data_name, r, ""
        if data_type == "keyed":
            print("keyed defn")
            # [
            #     "keyed",
            #     1,
            #     "Command response flag",
            #     {
            #         "00": "OK",
            #         "01": "Unknown ID",
            #         "02": "Not supported",
            #         "04": "Parameter Error",
            #     },
            # ],
            key = ""
            for x in raw_value:
                key += f"{x:02x}"
            if key in data_units:
                r = data_units[key]
            else:
                r = f"Invalid key: {key}"
            return data_name, r, ""
        if data_type == "str_keyed":
            print("str_keyed defn")
            # [
            #     "str_keyed",
            #     "Device Mode",
            #     {
            #         "B": "Inverter (Battery) Mode",
            #         "C": "PV charging Mode",
            #         "D": "Shutdown Mode",
            #         "F": "Fault Mode",
            #         "G": "Grid Mode",
            #         "L": "Line Mode",
            #         "P": "Power on Mode",
            #         "S": "Standby Mode",
            #         "Y": "Bypass Mode",
            #     },
            # ]
            key = raw_value.decode()
            if key in data_units:
                r = data_units[key]
            else:
                r = f"Invalid key: {key}"
            return data_name, r, ""
        format_string = f"{data_type}(raw_value)"
        print(f"Processing format string {format_string}")
        try:
            r = eval(format_string)
        except ValueError as e:
            print(f"Failed to eval format {format_string} (returning 0), error: {e}")
            return data_name, 0, data_units
        except TypeError as e:
            log.warning(f"Failed to eval format {format_string}, error: {e}")
            return data_name, format_string, data_units
        if template is not None:
            r = eval(template)
        if "{" in data_name:
            f = frame_number  # noqa: F841
            data_name = eval(data_name)
        return data_name, r, data_units

    def decode(self, response, command) -> dict:
        """
        Take the raw response and turn it into a dict of name: value, unit entries
        """

        print(f"response passed to decode: {response}")

        valid, msgs = self.check_response_valid(response)
        if not valid:
            print(msgs["ERROR"][0])
            return msgs

        # Add Raw response
        _response = b""
        for item in response:
            if type(item) is int:
                _response += chr(item).encode()
            else:
                _response += item.encode()
        raw_response = _response.decode("utf-8")
        msgs["raw_response"] = [raw_response, ""]

        # Add metadata
        msgs["_command"] = command
        # Check for a stored command definition
        command_defn = self.get_command_defn(command)
        if command_defn is not None:
            msgs["_command_description"] = command_defn["description"]
            len_command_defn = len(command_defn["response"])
        else:
            # No definition, so just return the data
            len_command_defn = 0
            print(
                f"No definition for command {command}, (splitted) raw response returned"
            )
            msgs["WARNING"] = [
                f"No definition for command {command} in protocol {self._protocol_id}",
                "",
            ]
            msgs["response"] = [raw_response, ""]
            return msgs

        # Determine the type of response
        if "response_type" in command_defn:
            response_type = command_defn["response_type"]
        else:
            response_type = "DEFAULT"
        print(f"Processing response of type {response_type}")

        # Split the response into individual responses
        responses = self.get_responses(response)
        print(f"trimmed and split responses: {responses}")

        # Decode response based on stored command definition and type
        # process default response type
        # TODO: fix this - move into new approach
        # DEFAULT - responses are determined by the order they are returned
        if response_type == "DEFAULT":
            print("Processing DEFAULT type responses")
            # print("Processing DEFAULT type responses")
            for i, result in enumerate(responses):
                # decode result
                if type(result) is bytes:
                    result = result.decode("utf-8")

                # Check if we are past the 'known' responses
                if i >= len_command_defn:
                    resp_format = ["string", f"Unknown value in response {i}", ""]
                else:
                    resp_format = command_defn["response"][i]

                # key = "{}".format(resp_format[1]).lower().replace(" ", "_")
                key = resp_format[1]
                # print(f'result {result}, key {key}, resp_format {resp_format}')
                # Process results
                if result == "NAK":
                    msgs[f"WARNING{i}"] = [
                        f"Command {command} was rejected",
                        "",
                    ]
                elif resp_format[0] == "float":
                    try:
                        result = float(result)
                    except ValueError:
                        print(f"Error resolving {result} as float")
                    msgs[key] = [result, resp_format[2]]
                elif resp_format[0] == "int":
                    try:
                        result = int(result)
                    except ValueError:
                        print(f"Error resolving {result} as int")
                    msgs[key] = [result, resp_format[2]]
                elif resp_format[0] == "string":
                    msgs[key] = [result, resp_format[2]]
                elif resp_format[0] == "10int":
                    if "--" in result:
                        result = 0
                    msgs[key] = [float(result) / 10, resp_format[2]]
                # eg. ['option', 'Output source priority', ['Utility first', 'Solar first', 'SBU first']],
                elif resp_format[0] == "option":
                    msgs[key] = [resp_format[2][int(result)], ""]
                # eg. ['keyed', 'Machine type', {'00': 'Grid tie', '01': 'Off Grid', '10': 'Hybrid'}],
                elif resp_format[0] == "keyed":
                    msgs[key] = [resp_format[2][result], ""]
                # eg. ['flags', 'Device status', [ 'is_load_on', 'is_charging_on' ...
                elif resp_format[0] == "flags":
                    for j, flag in enumerate(result):
                        # if flag != "" and flag != b'':
                        msgs[resp_format[2][j]] = [int(flag), "bool"]
                # eg. ['stat_flags', 'Warning status', ['Reserved', 'Inver...
                elif resp_format[0] == "stat_flags":
                    output = ""
                    for j, flag in enumerate(result):
                        # only display 'enabled' flags
                        # if flag == "1" or flag == b"1":
                        #    output = "{}\n\t- {}".format(output, resp_format[2][j])
                        # display all flags
                        key = resp_format[2][j]
                        output = flag
                        if key:  # only add msg if key is something
                            msgs[key] = [output, ""]
                # eg. ['enflags', 'Device Status', {'a': {'name': 'Buzzer', 'state': 'disabled'},
                elif resp_format[0] == "enflags":
                    # output = {}
                    status = "unknown"
                    for item in result:
                        if item == "E":
                            status = "enabled"
                        elif item == "D":
                            status = "disabled"
                        else:
                            # output[resp_format[2][item]['name']] = status
                            # _key = "{}".format(resp_format[2][item]["name"]).lower().replace(" ", "_")
                            if resp_format[2].get(item, None):
                                _key = resp_format[2][item]["name"]
                            else:
                                _key = "unknown_{}".format(item)
                            msgs[_key] = [status, ""]
                    # msgs[key] = [output, '']
                elif resp_format[0] == "multi":
                    for x, item in enumerate(result):
                        item_value = int(item)
                        item_resp_format = resp_format[1][x]
                        item_type = item_resp_format[0]
                        # print(x, item_value, item_resp_format, item_type)
                        if item_type == "option":
                            item_name = item_resp_format[1]
                            resolved_value = item_resp_format[2][item_value]
                            msgs[item_name] = [resolved_value, ""]
                        elif item_type == "string":
                            item_name = item_resp_format[1]
                            msgs[item_name] = [item_value, ""]
                        else:
                            print(f"item type {item_type} not defined")
                elif command_defn["type"] == "SETTER":
                    # _key = "{}".format(command_defn["name"]).lower().replace(" ", "_")
                    _key = command_defn["name"]
                    msgs[_key] = [result, ""]
                else:
                    print(f"Processing unknown response format {result}")
                    msgs[i] = [result, ""]
            return msgs

        # Check for multiple frame type responses
        if response_type == "MULTIFRAME-POSITIONAL":
            print("Processing MULTIFRAME-POSITIONAL type responses")
            # MULTIFRAME-POSITIONAL - multiple frames of responses are not separated and are determined by the position in the response
            # each frame has the same definition
            frame_count = len(responses)
            print(f"got {frame_count} frames")
            # the responses are the frames
            frames = responses
        else:
            frames = [responses]
            frame_count = 1

        for frame_number, frame in enumerate(frames):

            for i, response in enumerate(frame):
                if response_type == "KEYED":
                    print("Processing KEYED type responses")
                    # example defn ["V", "Main or channel 1 (battery) voltage", "V", "float:r/1000"]
                    # example response data [b'H1', b'-32914']
                    if len(response) <= 1:
                        # Not enough data in response, so ignore
                        continue
                    lookup_key = response[0]
                    raw_value = response[1]
                    response_defn = get_resp_defn(lookup_key, command_defn["response"])
                    if response_defn is None:
                        # No definition for this key, so ignore???
                        log.warn(f"No definition for {response}")
                        continue
                    # key = response_defn[0] #0
                    data_type = response_defn[3]  # 1
                    data_name = response_defn[1]  # 2
                    data_units = response_defn[2]  # 3

                elif response_type == "SEQUENTIAL":
                    print("Processing SEQUENTIAL type responses")
                    # check for extra definitions...
                    extra_responses_needed = len(command_defn["response"]) - len(frame)
                    if extra_responses_needed > 0:
                        for _ in range(extra_responses_needed):
                            frame.append("extra")
                    # example ["int", "Energy produced", "Wh"]

                    # Check if we are past the 'known' responses
                    if i >= len_command_defn:
                        response_defn = ["str", f"Unknown value in response {i}", ""]
                    else:
                        response_defn = command_defn["response"][i]
                    print(f"Got defn {response_defn}")
                    raw_value = response
                    # spacer = response_defn[0] #0
                    data_type = response_defn[0]  # 1
                    data_name = response_defn[1]  # 2
                    data_units = response_defn[2]  # 3

                    # print(f"{data_type=}, {data_name=}, {raw_value=}")
                elif response_type in ["POSITIONAL", "MULTIFRAME-POSITIONAL"]:
                    print("Processing POSITIONAL type responses")
                    # check for extra definitions...
                    extra_responses_needed = len(command_defn["response"]) - len(frame)
                    if extra_responses_needed > 0:
                        for _ in range(extra_responses_needed):
                            frame.append("extra")
                    # POSITIONAL - responses are not separated and are determined by the position in the response
                    # example defn :
                    #   ["discard", 1, "start flag", ""],
                    #   ["BigHex2Short", 2, "Battery Bank Voltage", "V"],
                    # example response data:
                    #   [b'\xa5', b'\x01', b'\x90', b'\x08', b'\x01\t', b'\x00\x00', b'u\xcf', b'\x03\x99', b'']
                    raw_value = response
                    # Check if we are past the 'known' responses
                    if i >= len_command_defn:
                        response_defn = ["str", 1, f"Unknown value in response {i}", ""]
                    else:
                        response_defn = command_defn["response"][i]
                    if response_defn is None:
                        # No definition for this key, so ignore???
                        log.warn(f"No definition for {response}")
                        response_defn = [
                            "str",
                            1,
                            f"Undefined value in response {i}",
                            "",
                        ]
                    print(f"Got defn {response_defn}")
                    # length = response_defn[1] #0
                    data_type = response_defn[0]  # 1
                    data_name = response_defn[2]  # 2
                    data_units = response_defn[3]  # 3

                # Check for lookup
                if data_type.startswith("lookup"):
                    print("processing lookup...")
                    print(
                        f"Processing data_type: '{data_type}' for data_name: '{data_name}', raw_value '{raw_value}'"
                    )
                    m = msgs
                    template = data_type.split(":", 1)[1]
                    print(f"Got template {template} for {data_name} {raw_value}")
                    lookup = eval(template)
                    print(f"looking up values for: {lookup}")
                    value, data_units = m[lookup]
                elif data_type.startswith("info"):
                    print("processing info...")
                    # print(
                    #    f"Processing {data_type=} for {data_name=}, {data_units=} {response=} {command=} {self._command_value=}"
                    # )
                    template = data_type.split(":", 1)[1]
                    # Provide cv as shortcut to self._command_value for info fields
                    cv = self._command_value  # noqa: F841
                    value = eval(template)
                else:
                    # Process response
                    data_name, value, data_units = self.process_response(
                        data_name=data_name,
                        raw_value=raw_value,
                        data_units=data_units,
                        data_type=data_type,
                        frame_number=frame_number,
                    )
                # print(data_type, data_name, raw_value, value)
                if data_name is not None:
                    msgs[data_name] = [value, data_units]
            # print(f"{i=} {response=} {len(command_defn['response'])}")

        return msgs
    
