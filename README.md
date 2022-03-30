# What is this

Clone/pull students repositories


# How to Use

## Prepare configuration file

Create configuration file or use the default one (`./config.json`).

The configuration file should be written in JSON:

```
{
    "csv_file_name": "data.csv",
    "result_dir_name": "data",
    "new_line": "",
    "delimiter": ",",
    "quote_char": "'"
}
```

Please take note, that the `csv_file_name` is `data.csv`. You should provide this file before running the script.

## Create csv file

Create a csv file containing student's name and their github repositories. The file name should match the one you define in the configuration (by default, it is `data.csv`):

```bash
EREN JEAGER,https://github.com/***/***.git
NARUTO UZUMAKI,https://github.com/***/***.git
KENSHIN HIMURA,https://github.com/***/***.git
```

## Run the script

```bash
python ./fetcher.py ./config.json
# or
# python ./fetcher.py
```

# Result

The git repositories should be cloned into `result_dir_name` directory:

```
.
├── README.md
├── config.json
├── data
│   ├── erenJeager
│   ├── narutoUzumaki
│   └── kenshinHimura
├── data.csv
└── fetcher.py
```