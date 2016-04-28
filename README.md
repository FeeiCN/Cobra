# Cobra

Static code analysis common security issues and scan common security vulnerabilities

### Scan Types

#### 1. Diff Scan

By comparing with the online code or the previous submission to find out the change code, and then only the changes to scan the code.

Advantages and disadvantages: 
Scanning speed, can immediately know the results of the scan. But the scanning range is small.

Scene: 
for the daily release, we need to quickly know that this is the existence of the risk of the code, using the contrast scan will be able to know the results for the first time.

#### 2. Full Scan
Description: by playing the compression package or send Git/SVN address, decompression, download the project will be all the code for the full scan.
Advantages and disadvantages: the scan speed is slow, but a comprehensive scan.
Scene: the whole volume scan can be used for items that are not frequently published in history.

### The development of language and support framework
In view of our current online projects mainly for PHP and JAVA, so we will support the two languages in a period.
And do a good job of our current framework for compatibility, to ensure that we can cover most of the business online.

Developer of Language|Framework
--- | ---
PHP|	Kohana、Laravel
JAVA|	Spring、Struts

### Supported vulnerability types
A major sweep some of the more common and difficult to put an end to the loopholes, the follow-up to support a number of dynamic scanning.

Item | Remark
--- | ---
XSS	|Cross-Site Scripting
CSRF|	Cross-site request forgery
SQL Injection|	SQL Injection
Sensitive Data Exposure|Sensitive Info Exposure、Back File Exposure、Code Exposure、Server Info Exposure、SVN/GIT Exposure...
WebShell	|WebShell
Backdoor | 
torjor|	Big torjor、Small torjor
URL Redirector Abuse	|
Misconfiguration|
LFI/RFI|	Local File Inclusion、Remote File Inclusion
Command Execution|
Code Execution|
Header Injection|

##### To be supported by the type of vulnerability (follow-up plan to gradually access)
Item|Remark
--- | ---
Variable Coverage	|
CRLF Injection CRLF|
Unauthorized Access|
Weak Password	|
XML Injection	|
Brute Force	|
