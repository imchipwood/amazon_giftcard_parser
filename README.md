# Amazon "Print At Home" Gift Card PDF Parser

Extracts out claim codes from Amazon gift card PDFs

## Usage

### --input_file/-i

Optional path to text file with directories and/or paths to PDF files. If not provided, looks for file named "paths.txt"
in the main directory

### --walk_dirs/-w

Enables recursively walking directories to find more PDFs

### --debug/-d

Enable verbose logging

## Input File Format

One path per line, can comment out with `#` at beginning of line

Example:

```text
/some/directory/with/pdfs
#/this/line/is/commented/out
/some/path/to/a/file.pdf
```