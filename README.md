# jctlfmt

[![GitHub main workflow](https://img.shields.io/github/actions/workflow/status/dmotte/jctlfmt/main.yml?branch=main&logo=github&label=main&style=flat-square)](https://github.com/dmotte/jctlfmt/actions)
[![PyPI](https://img.shields.io/pypi/v/jctlfmt?logo=python&style=flat-square)](https://pypi.org/project/jctlfmt/)

:snake: Python **Journalctl parsing** and **formatting** library.

With this library you can create custom scripts to **parse**, **filter** and **transform** data from **Journalctl** to a **human-friendly** format.

## Installation

This library is available as a Python package on **PyPI**:

```bash
python3 -mpip install jctlfmt
```

## Usage

You can use the `jctlfmt.Entry` class in your code to **parse** _Journalctl_ messages from **JSON format** and then you can create **your own formatter class** by extending `jctlfmt.BaseFormatter` to filter and print the entries in the format you like.

There is a full usage example in the [`example`](example) folder of this repo. To try it you can use the following commands:

```bash
ssh myuser@myserver.example.com "sudo journalctl -ojson --output-fields _SOURCE_REALTIME_TIMESTAMP,__REALTIME_TIMESTAMP,_HOSTNAME,_SYSTEMD_UNIT,_SYSTEMD_USER_UNIT,SYSLOG_IDENTIFIER,_PID,PRIORITY,MESSAGE -S '1 day ago'" > example/step01-json.txt
python3 example/dedup.py < example/step01-json.txt > example/step02-dedup.txt
python3 example/fmt.py < example/step02-dedup.txt > example/step03-fmt.txt
```

As you can see, there are two custom scripts: [`dedup.py`](example/dedup.py) (optional), which removes duplicate lines based on custom rules, and [`fmt.py`](example/fmt.py) which does the actual filtering and formatting.

You can also use [`fmt.py`](example/fmt.py) to explore _Journalctl_ logs on the go:

```bash
sudo journalctl -ojson -ussh -S '1 day ago' | python3 example/fmt.py -fs | less
```

Note that this time we invoke the script with `-fs` to disable filtering and sensitive mode. See `jctlfmt.BaseFormatter` for details.

You can customize [`fmt.py`](example/fmt.py) as you want and then use it in your setup. If you make modifications to the script and you want to test if the output is consistent, you can generate the output for all the possible invocations and then use `sha256sum` to check. The following commands may help:

```bash
for i in '' -f -fs -s; do
    python3 example/fmt.py $i < example/step02-dedup.txt > "example/step03-arg$i.txt"
done
sha256sum example/step03-arg*.txt | sha256sum
```

## Tips

:bulb: When **developing a custom formatter class** extended from `jctlfmt.BaseFormatter` (such as in [`fmt.py`](example/fmt.py)), it's recommended to design your _Python_ code as an **`if` tree** with **"match-return" branches**. Once you enter a branch, you should **never get out**, i.e. the code **should always return** for all the possible execution paths inside the branch. Example:

```python
if condition01:
    return something01
if condition02:
    if condition02_sub01:
        return something02_sub01
    if condition02_sub02:
        return something02_sub02
    return something02_default
if condition03:
    return something03
return something_default
```

As you can see, once the execution flow enters an `if` branch, it can't ever get out of it without returning something. As a result you are always sure that, **if a condition is matched, something will be returned based on that**.

With this approach the code is much **cleaner**, **clearer**, and **more maintainable**, as you **remove ambiguity** regarding "in which cases you enter a branch", and you are **less likely to miss cases**. Also the code is **simpler** and **more readable**, as you should never need to use `else` or `elif` anywhere.

## Development

If you want to contribute to this project, you can create a Python **virtual environment** ("venv") with the package in **editable** mode:

```bash
python3 -mvenv .venv
.venv/bin/python3 -mpip install -e .
```

This will link the package to the original location, so any changes to the code will reflect directly in your environment ([source](https://stackoverflow.com/a/35064498)).
