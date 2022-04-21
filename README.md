# wlan-api

## Running

```bash
python3 -m venv venv
pip install .

# Prepare config
export VOUCHER_PRIVATE_KEY=sql-generator/key.pem VOUCHER_CFG=sql-generator/voucher.cfg VOUCHER_BIN=sql-generator/voucher FLASK_SECRET=asdf MYSQL_HOST=localhost MYSQL_USER=user MYSQL_PASSWORD=password

FLASK_APP=wlan_api.server flask run
```

## Upgrading

This can be upgraded on the tuerantuer infrastructure using Salt.
