from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
PEP_PAGE = 'https://peps.python.org/'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
MISMATCH_STATUS_MESSAGE = (
    '\nНесовпадающие статусы: {pep_page}\n'
    'Статус в карточке: {status_pep}\n'
    'Ожидаемые статусы: {status}\n'
)
STATUS_COUNTS = 1
PREVIEW_STATUS = 1
ARCHIVE_SPLIT = -1
TOTAL_COUNT = 0
PATTERN_PYTHON = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
PATTERN_PDF = r'.+pdf-a4\.zip$'
CHOICE_PRETTY = 'pretty'
CHOICE_FILE = 'file'
LOG_DIR = 'logs'
DOWNLOAD_DIR = 'downloads'
RESULTS_DIR = 'results'
ENCODING = 'utf-8'


class Tags:
    LXML = 'lxml'
    SECTION = 'section'
    DIV = 'div'
    A = 'a'
    LI = 'li'
    HREF = 'href'
    DL = 'dl'
    H1 = 'h1'
    UL = 'ul'
    TABLE = 'table'
    TBODY = 'tbody'
    TR = 'tr'
    ABBR = 'abbr'
    DD = 'dd'
