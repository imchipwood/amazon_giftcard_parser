import argparse
import json
import logging
import os
import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError
import re
import sys
from typing import List

import library
from library.dir_helper import get_all_paths_from_file
global logger  # type: logging.Logger


def parse_args(args) -> argparse.Namespace:
    """
    Parse user arguments
    @param args:
    @type args:
    @return: parsed args
    @rtype: argparse.Namespace
    """
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
    return parser.parse_args(args)


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
    logger = library.get_logger(__name__, debug)

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
    args = parse_args(sys.argv[1:])
    parse_pdfs(args.input_file, args.walk_dirs, args.debug)
