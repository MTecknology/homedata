#!/usr/bin/python
"""Script for cleaning up diagnostics_historydump_bak rows.

NOTE: You need to set your mysql user and password as environment
      variables before using this script.
"""
import logging
import MySQLdb
import os
import sys
import time

# MySQL credentials
MYSQL_USER = os.environ["MYSQL_USER"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]

# MySQL database & table
MYSQL_DATABASE = "diagnostics"
MYSQL_TABLE = "diagnostics_historydump"

# Limit query to 2000 rows at a time
LIMIT = 10000
# Sleep time between each delete/drop
SLEEP_TIME = 10

# Location of diagnostics dump files
DUMPS_LOCATION = os.path.expanduser("~st/infrastructure/uploaded_files/dumps/")

def InitializeLogging():
  """Configure logging to console and optionally to disk."""
  logger = logging.getLogger("")
  logger.setLevel(logging.DEBUG)

  # All scripts log to console
  console = logging.StreamHandler()
  console.setLevel(logging.ERROR)
  formatter = logging.Formatter("%(levelname)-8s: %(message)s")
  console.setFormatter(formatter)
  logger.addHandler(console)

  log_filename = ConstructLogFilename()
  disk = logging.FileHandler(filename=log_filename, mode="a")
  #disk.setLevel(logging.DEBUG)
  disk.setLevel(logging.WARNING)
  formatter = logging.Formatter(
      "%(asctime)s.%(msecs).03d %(levelname)-8s %(message)s",
      "%Y-%m-%d %H:%M:%S")
  disk.setFormatter(formatter)
  logger.addHandler(disk)


def ConstructLogFilename():
  """Returns filename for logfile.

  Returns:
    Filename format <script_name>.Y-m-d-H-M-S
  """
  #base_name = os.path.basename(sys.argv[0])
  #pgm_name = os.path.splitext(base_name)[0]
  time_str = time.strftime("%Y-%m-%d-%H-%M-%S")

  filename = "infra_dump_cleanup.%s.log" % (time_str)

  return filename


def GetHistoryDumpRows(cursor):
  """Retreive the id, dump value from MYSQL_TABLE.

  Args:
    cursor: MySQLDB.cursor object

  Returns:
    Results of the query
  """
  sql = ("select id, dump from %s.%s "
         "where network_diagnostics_processed='p' "
         "and refactoring_processed='p' "
         "and sentry_reports_processed='p' "
         "order by id asc limit %s;" % (MYSQL_DATABASE, MYSQL_TABLE, LIMIT))
  cursor.execute(sql)

  return cursor.fetchall()


def DeleteDumpRow(db, cursor, row_id):
  """Delete a dump row.

  Args:
    db: MySQLdb object to diagnostics database
    cursor: MySQL cursor object
    row_id: Number ID of row
  """
  sql = "delete from %s.%s where id='%s';" % (
            MYSQL_DATABASE, MYSQL_TABLE, row_id)
  cursor.execute(sql)
  db.commit()

  logging.debug("Row %s has been deleted." % row_id)


def DeleteDumpFile(dump_file):
  """Delete a diagnostics dump file.

  Args:
    dump_file: Path to dump file
  """
  dump_file = dump_file.replace("dumps/", DUMPS_LOCATION)

  if os.path.exists(dump_file):
    logging.debug("Removing %s" % dump_file)
    os.remove(dump_file)
  else:
    logging.warning("File %s not found" % dump_file)


def StartDiagnosticsCleanup(db):
  """Continue looping until all rows matching the conditions are deleted.

  Args:
    db: MySQLdb object to diagnostics database
  """
  cursor = db.cursor()

  while(1):
    rows = GetHistoryDumpRows(cursor)
    if rows:
      for row in rows:
        row_id, dump_file = (int(row[0]), row[1])

        try:
          DeleteDumpFile(dump_file)
        except:
          logging.error("Unable to delete file %s." % dump_file)
          continue

        try:
          DeleteDumpRow(db, cursor, row_id)
        except:
          logging.error("Unable to delete row %s." % row_id)
          db.rollback()
          continue
    else:
      logging.info("Script is complete")
      break

    # Sleep for 2 seconds for IO reprieve
    logging.info("Script will now sleep for %s seconds." % SLEEP_TIME)
    time.sleep(SLEEP_TIME)


def main():
  InitializeLogging()
  logging.info("Starting diagnostics cleanup.")
  logging.info("Initializing DB connection...")
  db = MySQLdb.connect("localhost",
                       MYSQL_USER, MYSQL_PASSWORD,
                       MYSQL_DATABASE)
  cursor = db.cursor()
  logging.info("DB connection established")

  StartDiagnosticsCleanup(db)

  db.close()
  logging.info("Database connection closed.")


if __name__ == "__main__":
  main()
