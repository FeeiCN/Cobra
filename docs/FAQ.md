## python cobra.py start

* Q: Digest::MD5 not installed; will skip file uniqueness checks.
* A:
```
perl -MCPAN -e "shell"
> install Digest::MD5
```

## MySQL

|Code|Reason|
|---|---|
| 1146 | Datasheet does not exist, please go through the installation process (http://cobra-docs.readthedocs.io/en/latest/installation/) |
| 1048 | The field can not be NULL |
| 1045 | Account password is wrong|
| 1044 | The account password is correct, but there is no access to the DB |
| 1129 | The IP request to connect too much, use the `` `mysqladmin flush-hosts-p`` |

## Scan
* Q: The input SVN address can not be scanned
* A: There is a problem with SVN Checkout at this time. Please manually check SVN to local, and then use absolute path scan.

---
* Q: prompts the scan to complete, but did not sweep to any vulnerability
* A: Cobra is a set of scanning framework, you need to increase in the background for a variety of vulnerability scanning rules.

---
* Q: Key verify failed
* A: The secret_key in the config file is not configured