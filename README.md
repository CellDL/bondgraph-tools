# Tools for working with RDF descriptions of bondgraphs

### Installation pre-requisites

* Python 3.12
* [Poetry](https://python-poetry.org/) package manager
* Poetry's [Monoranger](https://github.com/ag14774/poetry-monoranger-plugin) plugin.

### Installation

```
$ git clone https://github.com/CellDL/bondgraph-tools.git
$ cd bondgraph-tools
$ poetry install
```

### Running

Activate the Python virtual environment:
```
$ source .venv/bin/activate
```

Command line help:
```
$ python rdf2cellml.py --help

usage: rdf2cellml.py [-h] [--version] [--celldl CELLDL_FILE] TEMPLATE_FILE MODEL_FILE CELLML_FILE

Generate CellML for a bondgraph model specified in RDF

positional arguments:
  TEMPLATE_FILE         A template file defining bondgraph components in RDF
  MODEL_FILE            The RDF definition of a model
  CELLML_FILE           The name for the resulting CellML file

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --celldl CELLDL_FILE  The name for the CellDL (SVG) output file. Optional
```
