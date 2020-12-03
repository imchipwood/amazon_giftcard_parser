import os
import re
from typing import List


def get_all_paths_from_file(path: str, walk: bool = False) -> List[str]:
    """
    Parse the input file and return all PDF paths
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
