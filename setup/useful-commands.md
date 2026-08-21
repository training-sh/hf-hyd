
failed attempts

```
sudo journalctl -u ssh --since "20 days ago" | grep -Ei 'failed password|invalid user' | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | sort | uniq -c | sort -nr
```
