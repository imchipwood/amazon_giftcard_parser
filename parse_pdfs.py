import argparse
import json
import logging
import os
import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError
import re
from typing import List

global logger  # type: logging.Logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Python 3.x Amazon Print-At-Home Gift Card parser - extracts claim codes"
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="input file path. Input file should have paths to directories with PDFs in them, "
             "or direct paths to PDFS"
    )
    parser.add_argument(
        "-w",
        "--walk_dirs",
        action="store_true",
        default=False,
        help="Walk into nested directories"
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug messages"
    )
    return parser.parse_args()


def get_all_paths_from_file(path: str, walk: bool = False) -> List[str]:
    """

    @param path: path to file with paths to read
    @type path: str
    @param walk: whether or not to walk into deeper directories
    @type walk: bool
    @return: list of all paths found by reading file and
    @rtype: list[str]
    """
    with open(path, 'r') as inf:
        paths = [x.strip() for x in inf.readlines()]

    uncommented_paths = [path for path in paths if path[0] != "#"]
    actual_paths = []
    for path in uncommented_paths:
        if not os.path.exists(path):
            continue
        if os.path.isdir(path):
            actual_paths.extend(_walk_path(path, walk))
        else:
            actual_paths.append(path)

    return actual_paths


def is_pdf(filename: str) -> bool:
    """
    Check if a file is a PDF
    @param filename: name of file
    @type filename: str
    @return: whether or not file extension is PDF
    @rtype: bool
    """
    _, ext = os.path.splitext(filename)
    return bool(re.search(r"pdf", ext, re.I))


def _walk_path(path: str, walk: bool = False) -> List[str]:
    """
    Walk a path and find PDFs in it
    @param path: path to find PDFs in
    @type path: str
    @param walk: whether or not to walk into deeper directories
    @type walk: bool
    @return: list of all paths found by reading file and
    @rtype: list[str]
    """
    actual_paths = []
    for root, dirs, files in os.walk(path):

        if root == path:
            for filename in files:
                if is_pdf(filename):
                    actual_paths.append(os.path.join(root, filename))

        if not walk:
            break

        for dirname in dirs:
            actual_paths.extend(_walk_path(os.path.join(root, dirname), walk))

    return actual_paths


def get_claim_from_pdf(pdf_path: str) -> str or None:
    """
    Parse PDF for claim number
    @param pdf_path: path to PDF file
    @type pdf_path: str
    @return: claim code from PDF
    @rtype: str or None
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]

            tables = first_page.find_tables()
            if not tables:
                logger.warning(f"Couldn't find tables for {pdf_path}")
                return None

            page = tables[0].page
            text = page.extract_text().split("\n")

            line_number = -1
            for i, line in enumerate(text):
                if re.search(r"claim code", line, re.I):
                    line_number = i + 1
                    break

            if line_number >= 0:
                return text[line_number].strip()

            logger.warning(f"Failed to find claim code for {pdf_path}")
            return None

    except PDFSyntaxError as e:
        logger.exception(f"Failed to parse {pdf_path}")
        return None


def get_logger(debug: bool = False) -> logging.Logger:
    """
    Set up loggers
    @param debug: flag to enable debug prints
    @type debug: bool
    @return: logger to use
    @rtype: logging.Logger
    """
    debug_level = logging.DEBUG if debug else logging.INFO
    new_logger = logging.getLogger(__name__)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(debug_level)
    stdout_format = "[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
    stdout_formatter = logging.Formatter(stdout_format)
    stream_handler.setFormatter(stdout_formatter)
    new_logger.handlers = []
    new_logger.addHandler(stream_handler)
    new_logger.propagate = False

    pdf_logger = logging.getLogger(pdfplumber.__name__)
    pdf_logger.setLevel(logging.WARN)
    pdf_logger.propagate = False

    new_logger.setLevel(debug_level)

    return new_logger


def parse_pdfs(input_file: str, walk_dirs: bool = False, debug: bool = False) -> List[str]:
    """
    Parse the PDFs and print the results
    @param input_file: path to input file with PDF paths/directories
    @type input_file: str
    @param walk_dirs: Enable parsing inner directories
    @type walk_dirs: bool
    @param debug: Enable verbose logging
    @type debug: bool
    @return: list of codes
    @rtype: list[str]
    """
    global logger
    logger = get_logger(debug)

    pdfs = get_all_paths_from_file(input_file, walk_dirs)

    num_pdfs = len(pdfs)
    logger.info(f"Found {num_pdfs} PDFs")
    logger.debug(json.dumps(pdfs, indent=2))

    codes = []
    for i, pdf in enumerate(pdfs):
        logger.info(f"reading pdf {i + 1}/{num_pdfs}")
        code = get_claim_from_pdf(pdf)
        if code:
            codes.append(code)

    raw_codes = "Codes:\n" + "\n".join(codes) + "\n"
    logger.info(raw_codes)
    num_codes = len(codes)
    if num_codes != num_pdfs:
        missing = num_pdfs - num_codes
        logger.warning(f"Failed to parse {missing} PDFs! See logs for details")
    return codes


if __name__ == "__main__":
    args = parse_args()
    parse_pdfs(args.input_file, args.walk_dirs, args.debug)
