# Amazon "Print At Home" Gift Card PDF Parser

Extracts out claim codes from Amazon gift card PDFs

# Requirements

Only requires Python3 (tested on Python3.8) and the `pdfplumber` package.


## Install required packages using pip

Using a virtual environment is recommended:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


# Usage

PDFs must be available on some local drive. The easiest method is to simply put them 
all in a single folder, but you can provide multiple directories or paths 
through an input file.

Example:
```bash
# standard mode
/path/to/your/venv/bin/python /path/to/amazon_gc_claim/main.py /path/to/input_file.txt
# walk inner directories
/path/to/your/venv/bin/python /path/to/amazon_gc_claim/main.py /path/to/input_file.txt -w
# enable verbose logging
/path/to/your/venv/bin/python /path/to/amazon_gc_claim/main.py /path/to/input_file.txt -d
```

## Command Line Arguments

### `input_file`

Path to text file with directories and/or paths to PDF files.

### `--walk_dirs` or `-w`

(Optional) Enables recursively walking directories to find more PDFs. 
If not enabled, will not walk inner directories.

### `--debug` or `-d`

(Optional) Enable verbose logging

## Input File Format

One path per line, can comment out with `#` at beginning of line

Example:

```text
/some/directory/with/pdfs
#/this/line/is/commented/out
/some/path/to/a/file.pdf
```