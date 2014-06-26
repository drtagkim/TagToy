'''
KICKSTARTER SERVER SETTING
AUTHOR: DRTAGKIM
2014
'''
# GENERAL SETTING ===============================
DATABASE_NAME = "sample.db" #SQLite3 database name (main)
QUIETLY = False
HAS_IMAGE = False

PROJECT_LOG_START_HOUR = '0' # project log starts at
PROJECT_LOG_START_MIN = '0' #0-59
PROJECT_LOG_START_SEC = '0' #0-59

PROJECT_PAGE_START_HOUR = '10'
PROJECT_PAGE_START_MIN = '0'
PROJECT_PAGE_START_SEC = '0'

VACUUM_DATABASE_HOUR = '23'
VACUUM_DATABASE_MIN = '0'
VACUUM_DATABASE_SEC = '0'

# PROJECT_LOG_SERVER SETTING ====================
# Data collection range. If True, full collection (from the beginning); othersie, False
SCRAP_FULL = False
# Page call again if the server responses too late.
PAGE_REQUEST_TRIAL = 10 # how many calls if it fails?
PROJECT_LOG_PORT = 1001
PROJECT_LOG_SERVER_THREAD_POOL = 13
CATEGORIES = ["1","2","3","4","5","6","7","8","9","10","11","12","13"]
# PROJECT_PAGE_SERVER SETTING ===================
PROJECT_PAGE_PORT = 1002
PROJECT_PAGE_SERVER_THREAD_POOL = 10
READ_LAG_TOLERANCE = 0 # second