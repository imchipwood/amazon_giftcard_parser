import os
import pytest

import library
from library.dir_helper import get_all_paths_from_file
import parse_pdfs

test_dir = os.path.dirname(__file__)
input_files_dir = os.path.join(test_dir, "input_files")
base_path = os.path.join(input_files_dir, "pdfs_dir")

input_file_name_000 = "test_paths_000.txt"
input_file_name_001 = "test_paths_001.txt"
input_file_name_002 = "test_paths_002.txt"
input_file_000 = os.path.join(input_files_dir, input_file_name_000)
input_file_001 = os.path.join(input_files_dir, input_file_name_001)
input_file_002 = os.path.join(input_files_dir, input_file_name_002)
input_files = {
    input_file_000: [
        base_path
    ],
    input_file_001: [
        os.path.join(base_path, "real_pdf_000.pdf"),
        os.path.join(base_path, "dir1")
    ],
    input_file_002: [
        "#" + os.path.join(base_path, "real_pdf_000.pdf"),
        os.path.join(base_path, "dir2", "real_pdf_002.pdf"),
        os.path.join(base_path, "dir2", "nonexistent_pdf_000.pdf")
    ]
}

real_pdf_path_000 = os.path.join(base_path, "real_pdf_000.pdf")
real_pdf_path_001 = os.path.join(base_path, "dir1", "real_pdf_001.pdf")
real_pdf_path_002 = os.path.join(base_path, "dir2", "real_pdf_002.pdf")
bad_pdf_path_000 = os.path.join(base_path, "dir1", "bad.pdf")
bad_pdf_path_001 = os.path.join(base_path, "dir2", "other_bad.pdf")

claim_code_000 = "9XNK-3TRPUC-HFAC"
claim_code_001 = "YSQM-VTWEBN-4WAA"
claim_code_002 = "65B7-8M26V9-7KAQ"


def create_input_path_files():
    for file_name, paths in input_files.items():
        if os.path.exists(file_name):
            os.remove(file_name)
        with open(file_name, 'w') as oup:
            oup.write("\n".join(paths))


def remove_input_path_files():
    for file_name in input_files.keys():
        if os.path.exists(file_name):
            os.remove(file_name)


def setup_module():
    create_input_path_files()
    parse_pdfs.logger = library.get_logger("parse_pdfs")


def teardown_module():
    remove_input_path_files()


@pytest.mark.parametrize(
    "input_file,walk_dirs,expected_files", [
        (input_file_name_000, False, [real_pdf_path_000]),
        (input_file_name_000, True, [real_pdf_path_000, real_pdf_path_001, real_pdf_path_002, bad_pdf_path_000, bad_pdf_path_001]),
        (input_file_name_001, False, [real_pdf_path_000, real_pdf_path_001, bad_pdf_path_000]),
        (input_file_name_001, True, [real_pdf_path_000, real_pdf_path_001, bad_pdf_path_000]),
        (input_file_name_002, False, [real_pdf_path_002]),
        (input_file_name_002, True, [real_pdf_path_002]),
    ]
)
def test_get_all_paths_from_file(input_file, walk_dirs, expected_files):
    paths = get_all_paths_from_file(os.path.join(input_files_dir, input_file), walk_dirs)
    assert set(paths) == set(expected_files)


@pytest.mark.parametrize(
    "pdf_path,expected_claim_code", [
        (real_pdf_path_000, claim_code_000),
        (real_pdf_path_001, claim_code_001),
        (real_pdf_path_002, claim_code_002),
        (bad_pdf_path_000, None),
        (bad_pdf_path_001, None),
    ]
)
def test_get_claim_from_pdf(pdf_path, expected_claim_code):
    claim_code = parse_pdfs.get_claim_from_pdf(pdf_path)
    assert claim_code == expected_claim_code


@pytest.mark.parametrize(
    "input_file,walk_dirs,expected_claim_codes", [
        (input_file_name_000, False, [claim_code_000]),
        (input_file_name_000, True, [claim_code_000, claim_code_001, claim_code_002]),
        (input_file_name_001, False, [claim_code_000, claim_code_001]),
        (input_file_name_001, True, [claim_code_000, claim_code_001]),
        (input_file_name_002, False, [claim_code_002]),
        (input_file_name_002, True, [claim_code_002]),
    ]
)
def test_parse_pdfs(input_file, walk_dirs, expected_claim_codes):
    codes = parse_pdfs.parse_pdfs(os.path.join(input_files_dir, input_file), walk_dirs)
    assert set(codes) == set(expected_claim_codes)


def test_parse_args():
    args = parse_pdfs.parse_args([input_file_000, '-w', '-d'])
    assert args.input_file == input_file_000
    assert args.walk_dirs
    assert args.debug
