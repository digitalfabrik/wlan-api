# wlan-api

## Running

```bash
python3 -m venv venv
pip install .

# Prepare config
export FLASK_SECRET=asdf MYSQL_HOST=localhost MYSQL_USER=user MYSQL_PASSWORD=password

FLASK_APP=wlan_api.server flask run
```

## Upgrading

This can be upgraded on the tuerantuer infrastructure using Salt.
