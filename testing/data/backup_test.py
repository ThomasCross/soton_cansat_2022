from CFS.Data.logger import setup_logging
from CFS.Data.backups import Backup

setup_logging("backup_testing")

# Creation Test
backup_data = Backup('backup_testing', 'M:\\Programming\\Github\\soton_cansat\\testing\\data\\')

# Write
backup_data.write("test line 1")
backup_data.write("test line 2")
backup_data.write("test line 3")
backup_data.write("test line 4")

# Close
backup_data.stop()


