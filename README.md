# VPG

## Running

```bash
# Prepare config
export VOUCHER_PRIVATE_KEY=sql-generator/key.pem VOUCHER_CFG=sql-generator/voucher.cfg VOUCHER_BIN=sql-generator/voucher FLASK_SECRET=asdf

FLASK_APP=vpg.server flask run
```

## Upgrading

This can be upgraded on the tuerantuer infrastructure using Salt.
