# jctlfmt

[![GitHub main workflow](https://img.shields.io/github/actions/workflow/status/dmotte/jctlfmt/main.yml?branch=main&logo=github&label=main&style=flat-square)](https://github.com/dmotte/jctlfmt/actions)
[![PyPI](https://img.shields.io/pypi/v/jctlfmt?logo=python&style=flat-square)](https://pypi.org/project/jctlfmt/)

:snake: Python **Journalctl parsing** and **formatting** library.

With this library you can create custom scripts to **parse**, **filter** and **transform** data from **Journalctl** in a **human-friendly** format.

## Installation

This library is available as a Python package on **PyPI**:

```bash
python3 -mpip install jctlfmt
```

## Usage

You can use the `jctlfmt.Entry` class in your code to **parse** _Journalctl_ messages from **JSON format** and then you can create **your own formatter class** by extending `jctlfmt.BaseFormatter` to filter and print the entries in the format you like.

I have put a full usage example in the [`example`](example) folder of this repo. To try it you can use the following commands:

```bash
ssh myuser@myserver.example.com "sudo journalctl -ojson --output-fields _SOURCE_REALTIME_TIMESTAMP,__REALTIME_TIMESTAMP,_HOSTNAME,_SYSTEMD_UNIT,SYSLOG_IDENTIFIER,_PID,PRIORITY,MESSAGE -S '1 day ago'" > example/step01-json.txt
python3 example/dedup.py < example/step01-json.txt > example/step02-dedup.txt
python3 example/fmt.py < example/step02-dedup.txt > example/step03-fmt.txt
```

As you can see I have two custom scripts: [`dedup.py`](example/dedup.py), which removes duplicate lines based on custom rules, and [`fmt.py`](example/fmt.py) which does the actual filtering and formatting.

In alternative, you can also use [`fmt.py`](example/fmt.py) to explore _Journalctl_ logs on the go:

```bash
sudo journalctl -ojson -ussh -S '1 day ago' | python3 example/fmt.py -fs | less
```

As you can see, this time I invoked the script with `-fs` to disable filtering and sensitive mode. See `jctlfmt.BaseFormatter` for details.

You can customize [`fmt.py`](example/fmt.py) as you want and then use it in your setup. If you make modifications to the script and you want to test if the output is consistent, you can generate the output for all the possible invocations and then use `sha256sum` to check. The following commands may help:

```bash
for i in '' -f -fs -s; do
    python3 example/fmt.py $i < example/step02-dedup.txt > "example/step03-arg$i.txt"
done
sha256sum example/step03-arg*.txt | sha256sum
```

## Development

If you want to contribute to this project, you can install the package in **editable** mode:

```bash
python3 -mpip install -e . --user
```

This will just link the package to the original location, basically meaning any changes to the original package would reflect directly in your environment ([source](https://stackoverflow.com/a/35064498)).
