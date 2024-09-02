import logging
import re
import requests_cache

from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin

from configs import configure_argument_parser, configure_logging
from constants import (ARCHIVE_SPLIT, BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL,
                       MISMATCH_STATUS_MESSAGE, PATTERN_PDF, PATTERN_PYTHON,
                       PEP_PAGE, PREVIEW_STATUS, STATUS_COUNTS, TOTAL_COUNT,
                       Tags)
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features=Tags.LXML)
    main_div = find_tag(soup, Tags.SECTION,
                        attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, Tags.DIV,
                           attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        Tags.LI, attrs={'class': 'toctree-l1'})
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, Tags.A)
        version_link = urljoin(whats_new_url, version_a_tag[Tags.HREF])
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features=Tags.LXML)
        h1 = find_tag(soup, Tags.H1)
        dl = find_tag(soup, Tags.DL)
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features=Tags.LXML)
    sidebar = find_tag(soup, Tags.DIV, attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all(Tags.UL)
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all(Tags.A)
            break
        raise Exception('Ничего не нашлось')
    pattern = PATTERN_PYTHON
    for a_tag in a_tags:
        link = a_tag[Tags.HREF]
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features=Tags.LXML)
    main_tag = find_tag(soup, Tags.DIV, {'role': 'main'})
    table_tag = find_tag(main_tag, Tags.TABLE, {'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, Tags.A,
                          {Tags.HREF: re.compile(PATTERN_PDF)})
    pdf_a4_link = pdf_a4_tag[Tags.HREF]
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[ARCHIVE_SPLIT]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    pep_url = urljoin(MAIN_DOC_URL, PEP_PAGE)
    response = get_response(session, pep_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features=Tags.LXML)
    section_tag = find_tag(soup, Tags.SECTION, attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, Tags.TBODY)
    tr_tags = tbody_tag.find_all(Tags.TR)
    status_counts = {}
    total_count = TOTAL_COUNT
    for tr in tqdm(tr_tags):
        first_column_tag = find_tag(tr, Tags.ABBR)
        preview_status = first_column_tag.text[PREVIEW_STATUS:]
        status = EXPECTED_STATUS.get(preview_status)
        pep_tag = find_tag(tr, Tags.A)[Tags.HREF]
        pep_page = urljoin(PEP_PAGE, pep_tag)
        response = session.get(pep_page)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features=Tags.LXML)
        dl_tag = find_tag(soup, Tags.DL)
        dl_tag_status = dl_tag.find(string='Status')
        status_pep = dl_tag_status.find_next(Tags.DD).text.strip()
        if status_pep not in status:
            logging.info(
                MISMATCH_STATUS_MESSAGE.format(
                    pep_page=pep_page,
                    status_pep=status_pep,
                    status=', '.join(status)
                )
            )
        if status_pep in status_counts:
            status_counts[status_pep] += STATUS_COUNTS
        else:
            status_counts[status_pep] = STATUS_COUNTS
        total_count += STATUS_COUNTS
    status_counts['Total'] = total_count
    results = [('Статус', 'Количество')]
    results.extend((status, count) for status, count in status_counts.items())
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
