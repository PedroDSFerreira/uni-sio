<div align="center">
    <h1>CWE-89</h1>
    <i>
        Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')
    </i>
</div>

<br>

## Description

The application does not properly sanitize user input before using it in an SQL query. 
<br>

## Exploit
Since the input is not sanitized, we can insert data in a way that, when the query is processed, malicious SQL commands are executed.

To test if this is possible in the search bar, we ran:

```sql
'
```

Since the popup didn't open, something happened, the query was broken.

The mentioned query is:
```sql
SELECT * FROM site_services WHERE name LIKE '%'
```

Then we tried to input a `True` condition:
```sql
' or 1 --
```

And this happened:

![](/analysis/CWE-89/1_insecure_query.gif)


Nice. Since the condition is always true, all items from the table were retrieved.

But this information isn't that relevant.

Then we used UNION SELECT:

```sql
' UNION SELECT 1,2,3 -- 
```
![image](https://user-images.githubusercontent.com/97121697/201823714-7e4e5e45-8b14-45f7-97ce-39a2c6b3ba2a.png)

This enables the attacker to display information on the popup, in this case, 2 and 3 (the first row is not being displayed)

What about sensitive information?


<br>

## Consequences

```sql
' UNION SELECT 1,2,sql FROM sqlite_schema -- 
```
![image](https://user-images.githubusercontent.com/97121697/201823625-ad54c264-9d94-4eb0-9d42-8bdc5d65623f.png)

Ops! We now know all DB table names, and table column names and types.

From this point on, we have access to all the information contained in the DB:


```sql
' UNION SELECT 1, file_path,code FROM site_test_results -- 
```
![image](https://user-images.githubusercontent.com/97121697/201824149-afaf9118-3bdb-4460-83b4-d042ead66eaf.png)

Even worse news, because of [CWE-312](CWE-312.md), we know all test result codes stored in the DB and, consequently, have access to all pdfs containing the client's health information.

Furthermore, the input `' or 1 --` in the "code" field of test results allows an attacker to have access to the first test result of the DB:

![](/analysis/CWE-89/2_insecure_query.gif)


<br>

## Mitigation

To prevent an SQL injection attack, **the query must always process the input as a string**.

In SQLite, we can use a **parameterized query**, so instead of:

```python
c.execute("SELECT * FROM site_test_results WHERE code = '%s'" % code)
```

We write:

```python
c.execute("SELECT * FROM site_test_results WHERE code = ?", (code,))
```

This makes it so that all input, regardless of the chars included, is always processed in the SQL query as a string.

Testing previously vulnerable fields, SQL injection now doesn't work.

![](/analysis/CWE-89/1_secure_query.gif)
![](/analysis/CWE-89/2_secure_query.gif)

---

<div align="center">
<i>
    <a href="/report/README.md">Back to report</a>
</i>
</div>
