
# Snowflake Key-Pair Authentication from Ubuntu and Airflow

## ***Use with care***

This guide configures **Snowflake key-pair authentication** on Ubuntu Linux, tests the connection using Python, and configures the same private key for Apache Airflow.

> **Important:** Replace values such as `linux_username`, `SNOWFLAKE_USERNAME`, `ACCOUNT_IDENTIFIER`, `COMPUTE_WH`, and `ECOMM_DB` with your own values.

---

## 1. Create a Directory for Snowflake Keys

Create a dedicated directory under the current Linux user's `.ssh` directory.

```bash
mkdir -p ~/.ssh/snowflake
chmod 700 ~/.ssh/snowflake
cd ~/.ssh/snowflake
```

---

## 2. Generate the Private Key

Generate a 2048-bit RSA private key in PKCS#8 format.

For this lab, the private key is created **without a passphrase**.

```bash
openssl genrsa 2048 | \
openssl pkcs8 \
  -topk8 \
  -inform PEM \
  -out snowflake_key.p8 \
  -nocrypt
```

Protect the private key:

```bash
chmod 600 snowflake_key.p8
```

Verify:

```bash
ls -l snowflake_key.p8
```

Check the beginning of the key:

```bash
head snowflake_key.p8
```

Expected:

```text
-----BEGIN PRIVATE KEY-----
```

Verify that the private key is valid:

```bash
openssl pkey \
  -in snowflake_key.p8 \
  -check \
  -noout
```

Expected:

```text
Key is valid
```

> **Security:** Never commit `snowflake_key.p8` to Git or share the private key.

---

## 3. Generate the Public Key

Generate the corresponding RSA public key:

```bash
openssl rsa \
  -in snowflake_key.p8 \
  -pubout \
  -out snowflake_key.pub
```

Verify:

```bash
cat snowflake_key.pub
```

The output should look similar to:

```text
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...
...
-----END PUBLIC KEY-----
```

---

## 4. Convert the Public Key to One-Line Format

Snowflake requires the Base64 public-key content without the `BEGIN PUBLIC KEY` and `END PUBLIC KEY` lines.

Run:

```bash
grep -v "BEGIN PUBLIC KEY" snowflake_key.pub \
  | grep -v "END PUBLIC KEY" \
  | tr -d '\n'
```

Alternatively, store it in a shell variable:

```bash
PUBLIC_KEY=$(grep -v "BEGIN PUBLIC KEY" snowflake_key.pub \
  | grep -v "END PUBLIC KEY" \
  | tr -d '\n')

echo "$PUBLIC_KEY"
```

The result will look similar to:

```text
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCA...
```

Copy this value.

---

## 5. Register the Public Key in Snowflake

Log in to Snowflake using a user with permission to alter the required Snowflake user.

Run:

```sql
ALTER USER SNOWFLAKE_USERNAME
SET RSA_PUBLIC_KEY='PASTE_PUBLIC_KEY_HERE';
```

For example:

```sql
ALTER USER MAILTOGOPS
SET RSA_PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...';
```

> Only the **public key** is registered with Snowflake. The private key must remain on the Linux machine.

Verify the configuration:

```sql
DESC USER SNOWFLAKE_USERNAME;
```

Look for:

```text
RSA_PUBLIC_KEY_FP
```

A fingerprint should be present.

---

# Test the Connection from Ubuntu

## 6. Find the Absolute Path of the Private Key

Linux shell commands can conveniently use `~`.

Applications such as Airflow should use the **absolute path** to the private key.

Find it using:

```bash
realpath ~/.ssh/snowflake/snowflake_key.p8
```

Example output:

```text
/home/linux_username/.ssh/snowflake/snowflake_key.p8
```

> Replace `linux_username` with the actual Linux username.

You can also determine the current username using:

```bash
whoami
```

---

## 7. Install the Snowflake Python Connector

Activate the Python virtual environment being used:

```bash
source /path/to/virtualenv/bin/activate
```

Install the connector:

```bash
pip install snowflake-connector-python
```

Verify:

```bash
pip show snowflake-connector-python
```

---

## 8. Test Snowflake Authentication Using Python

Create a test program:

```bash
nano test_snowflake.py
```

Add:

```python
import snowflake.connector

conn = snowflake.connector.connect(
    user="SNOWFLAKE_USERNAME",
    account="ACCOUNT_IDENTIFIER",
    private_key_file="/home/linux_username/.ssh/snowflake/snowflake_key.p8",
    role="ACCOUNTADMIN",
    warehouse="COMPUTE_WH",
    database="ECOMM_DB",
    schema="PUBLIC"
)

cur = conn.cursor()

try:
    cur.execute("""
        SELECT
            CURRENT_USER(),
            CURRENT_ROLE(),
            CURRENT_WAREHOUSE(),
            CURRENT_DATABASE(),
            CURRENT_SCHEMA()
    """)

    print(cur.fetchone())

finally:
    cur.close()
    conn.close()
```

Replace the following values with the appropriate values for your environment:

```text
SNOWFLAKE_USERNAME
ACCOUNT_IDENTIFIER
linux_username
ACCOUNTADMIN
COMPUTE_WH
ECOMM_DB
PUBLIC
```

Run:

```bash
python test_snowflake.py
```

A successful result will look similar to:

```text
('MAILTOGOPS', 'ACCOUNTADMIN', 'COMPUTE_WH', 'ECOMM_DB', 'PUBLIC')
```

This confirms that Snowflake key-pair authentication works independently of Airflow.

---

# Configure Snowflake in Apache Airflow

## 9. Install the Airflow Snowflake Provider

Activate the Python environment where Airflow is installed:

```bash
source /path/to/airflow_virtualenv/bin/activate
```

Install the Snowflake provider:

```bash
pip install apache-airflow-providers-snowflake
```

Verify:

```bash
airflow providers list | grep -i snowflake
```

---

## 10. Create the Snowflake Connection in Airflow

Open the Airflow UI and navigate to:

> **Admin → Connections**

Create a new connection.

Configure:

```text
Connection ID:   snowflake_default
Connection Type: Snowflake

Login:           SNOWFLAKE_USERNAME
Password:        <LEAVE COMPLETELY EMPTY>

Account:         ACCOUNT_IDENTIFIER
Warehouse:       COMPUTE_WH
Database:        ECOMM_DB
Schema:          PUBLIC
Role:            ACCOUNTADMIN
```

> **Important:** The Password field must be completely empty because the private key created in this guide is not encrypted.

---

## 11. Configure the Private Key in Airflow

First obtain the absolute private-key path:

```bash
realpath ~/.ssh/snowflake/snowflake_key.p8
```

Example:

```text
/home/linux_username/.ssh/snowflake/snowflake_key.p8
```

In the Airflow connection's **Extra** field, configure:

```json
{
  "private_key_file": "/home/linux_username/.ssh/snowflake/snowflake_key.p8"
}
```

Do **not** use this in Airflow:

```text
~/.ssh/snowflake/snowflake_key.p8
```

Use the absolute path returned by `realpath`.

---

## 12. Important: Leave the Airflow Password Empty

The private key was generated with:

```bash
-nocrypt
```

Therefore, it does **not** have a passphrase.

The Airflow connection must have:

```text
Password: <EMPTY>
```

Do not enter:

```text
Snowflake password
dummy password
private-key password
```

If a password is supplied while using the unencrypted private key, Airflow can fail with:

```text
TypeError: Password was given but private key is not encrypted.
```

If this error occurs, edit the Airflow connection and completely clear the Password field.

---

## 13. Verify the Airflow Connection

Activate the Airflow environment:

```bash
source /path/to/airflow_virtualenv/bin/activate
```

Display the configured connection:

```bash
airflow connections get snowflake_default
```

You can also check programmatically whether Airflow thinks a password exists.

Run Python:

```bash
python
```

Then:

```python
from airflow.sdk import Connection

conn = Connection.get("snowflake_default")

print("Login:", conn.login)
print("Password exists:", bool(conn.password))
print("Extra:", conn.extra)
```

The important result is:

```text
Password exists: False
```

If you get:

```text
Password exists: True
```

edit the Airflow connection and completely remove the password.

---

## 14. Check for Environment Variable Overrides

If the Airflow UI shows an empty password but Airflow still behaves as though a password exists, check whether an environment variable is overriding the connection.

```bash
env | grep -i AIRFLOW_CONN_SNOWFLAKE
```

Also check:

```bash
env | grep -i SNOWFLAKE
```

For example, an environment variable such as:

```text
AIRFLOW_CONN_SNOWFLAKE_DEFAULT=...
```

may provide a different connection configuration.

---

# Test from an Airflow DAG

## 15. Create a Snowflake Connection Test DAG

Create a DAG using `SQLExecuteQueryOperator`.

```python
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime

with DAG(
    dag_id="snowflake_connection_test",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    test_snowflake = SQLExecuteQueryOperator(
        task_id="test_snowflake",
        conn_id="snowflake_default",
        sql="""
            SELECT
                CURRENT_USER(),
                CURRENT_ROLE(),
                CURRENT_WAREHOUSE(),
                CURRENT_DATABASE(),
                CURRENT_SCHEMA();
        """
    )
```

Trigger the DAG from the Airflow UI or CLI:

```bash
airflow dags trigger snowflake_connection_test
```

Check the task logs for successful execution.

---

# Authentication Flow

The configuration is:

```text
                    Snowflake
                       │
                       │ Public Key
                       ▼
                Snowflake User
                       ▲
                       │
                RSA Authentication
                       │
             ┌─────────┴─────────┐
             │                   │
           Python              Airflow
             │                   │
             └─────────┬─────────┘
                       │
                  Private Key
                       │
                       ▼
 /home/linux_username/.ssh/snowflake/snowflake_key.p8
```

The **public key** is registered with Snowflake.

The **private key** remains on the Ubuntu machine and is used by Python or Airflow to authenticate.

---

# Final Checklist

Check the private key:

```bash
ls -l ~/.ssh/snowflake/snowflake_key.p8
```

Check the public key:

```bash
ls -l ~/.ssh/snowflake/snowflake_key.pub
```

Validate the private key:

```bash
openssl pkey \
  -in ~/.ssh/snowflake/snowflake_key.p8 \
  -check \
  -noout
```

Get the absolute path required by Airflow:

```bash
realpath ~/.ssh/snowflake/snowflake_key.p8
```

The complete setup should satisfy the following:

```text
✓ RSA private key generated
✓ RSA public key generated
✓ Public key registered with Snowflake
✓ Private key remains on Ubuntu
✓ Private key permissions set to 600
✓ Direct Python Snowflake connection works
✓ Airflow Snowflake provider installed
✓ Airflow connection uses the ab
```


