# yappr

Yet another python package updater

## Installation

You can install the package via pip:

```bash
pip install yappr
```

## Usage

```python
from yappr import Updater

u = Updater("httpx", first_update_interval=0)
u.check_for_updates_loop()

# 04/27/2024 02:35:14 AM - INFO - Checking for updates...
# 04/27/2024 02:35:19 AM - INFO - New version found: 0.23.2 -> 0.27.0
# 04/27/2024 02:35:19 AM - INFO - Collecting new packages...
# 04/27/2024 02:35:26 AM - INFO - Successfully downloaded new version.
```

## License

This project is licensed under the terms of the MIT license.
