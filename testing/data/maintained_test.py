from CFS.Data.logger import setup_logging
from CFS.Data.maintained import MaintainedData, MaintainedKeys

setup_logging("maintained_testing")

# Creation Test
maintained_data = MaintainedData('M:\\Programming\\Github\\soton_cansat\\testing\\data\\maintained_testing.txt')

# Write Tests
maintained_data.write_value(MaintainedKeys.MISSION_START_TIME, "2022-02-09 22:41:00")
maintained_data.write_value(MaintainedKeys.CONTAINER_PACKET, 5)
maintained_data.write_value(MaintainedKeys.CONTAINER_STATE, 6)
maintained_data.write_value(MaintainedKeys.PAYLOAD_PACKET, 10000)
maintained_data.write_value(MaintainedKeys.PAYLOAD_STATE, 2)
maintained_data.write_value(MaintainedKeys.LAUNCH_ALT, 100)
maintained_data.write_value(MaintainedKeys.CMD_ECHO, "CX101")

# Write Invalid Key Data
maintained_data.write_value("incorrect_key", "CX101")

# Read Tests
print("MST: {}".format(maintained_data.read_value(MaintainedKeys.MISSION_START_TIME, False)))
print("CP: {}".format(maintained_data.read_value(MaintainedKeys.CONTAINER_PACKET, True)))
print("PP: {}".format(maintained_data.read_value(MaintainedKeys.PAYLOAD_PACKET, False)))
print("CS: {}".format(maintained_data.read_value(MaintainedKeys.CONTAINER_STATE, True)))
print("PS: {}".format(maintained_data.read_value(MaintainedKeys.PAYLOAD_STATE, False)))
print("LA: {}".format(maintained_data.read_value(MaintainedKeys.LAUNCH_ALT, True)))
print("CE: {}".format(maintained_data.read_value(MaintainedKeys.CMD_ECHO, False)))

# Read Invalid Key Data
maintained_data.read_value("incorrect_key", False)
maintained_data.read_value("incorrect_key1", True)

# Reset Test
maintained_data.reset()

print("RST - MST: {}".format(maintained_data.read_value(MaintainedKeys.MISSION_START_TIME, False)))
print("RST - CP: {}".format(maintained_data.read_value(MaintainedKeys.CONTAINER_PACKET, True)))
print("RST - PP: {}".format(maintained_data.read_value(MaintainedKeys.PAYLOAD_PACKET, False)))
print("RST - CS: {}".format(maintained_data.read_value(MaintainedKeys.CONTAINER_STATE, True)))
print("RST - PS: {}".format(maintained_data.read_value(MaintainedKeys.PAYLOAD_STATE, False)))
print("RST - LA: {}".format(maintained_data.read_value(MaintainedKeys.LAUNCH_ALT, True)))
print("RST - CE: {}".format(maintained_data.read_value(MaintainedKeys.CMD_ECHO, False)))