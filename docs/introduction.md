# Orientation
Cobra is a static code analysis system that automates the detecting vulnerabilities and security issue.

If the vulnerability from the perspective of speaking, can be broadly divided into:

| Type | Impact Level | Impact Description | Typical Example | Typical Software|
| --- | --- | --- | --- | --- |
| Black Box | 100 | Available directly | SQL Injection, XXE, SSRF, etc. | [SQLMap](http://sqlmap.org/) |
| White Box 1 | 80 | May be used directly or indirectly or temporarily unavailable | A function that exists in SSRF, but may not be invoked when discovered | [RIPS](https://github.com/ripsscanner/rips)
| Whitebox 2 | 20 | Can not be used directly but is not compliant | Using functions that are deprecated due to security issues | [SonarQube](https://sonarqube.com/) |

The Cobra is positioned to cover white box 1 and white box 2 two levels:
1. Can find all the vulnerabilities in the code points (these vulnerabilities can not be directly used as a risk, because the existence of these risks, sooner or later there may be security incidents).
2. Can quickly respond to the scanning of new vulnerabilities.

### Why do we need a code audit system?

Companies are growing, more and more developers. Each R & D personnel are not the same quality of security, although the company's core projects can take ** framework layer security **, but too many new types of projects, each project can not be done using the same framework, Security component.

So all the projects for the company must have a protection to protect the basic security, code security audit can be used as a means of security.

### Industry research

At present the industry has a lot of code audit tools

| Name | Open Source | Estimate |
| ---------------------------------------- | ---- | --- |
| [Droopescan](https://github.com/droope/droopescan) | Yes | Override CMS framework only |
| [GrepBugs](https://grepbugs.com/) | Yes | Simple regular match, false positive |
| [Pixy](https://github.com/oliverklee/pixy) | Yes | Not Commercial, Immature |
| [RIPS](http://rips-scanner.sourceforge.net/) | Yes | Only PHP is covered|
| [SWAAT](https://www.owasp.org/index.php/Category:OWASP_SWAAT_Project) | Yes | .NET write, can not quickly expand new vulnerabilities |
| [PHP-SAT](http://www.program-transformation.org/PHP/PhpSat) | Yes | Overwrite PHP only, do not maintain for a long time, can not quickly expand new vulnerabilities |
| [Yasca](http://scovetta.github.io/yasca/) | Yes | Scanning for code security specs that can not quickly scale new vulnerabilities |
| [SonarQube](https://sonarqube.com/) | Yes | Scanning for code security specifications, rules exploiting Java code to quickly add new vulnerability scanning rules |
| [PreFast](http://msdn.microsoft.com/en-us/library/ms933794.aspx) | Yes | Only for C / C ++ |
| [PMD](http://pmd.sourceforge.net/) | Yes | Only for Java |
| [Google CodeSearchDiggity](https://www.bishopfox.com/resources/tools/google-hacking-diggity/attack-tools/) | Yes | Tools |
| [FxCop](http://msdn.microsoft.com/en-us/library/bb429476(VS.80).aspx) | Yes | For .NET |
| [Flawfinder](http://www.dwheeler.com/flawfinder/) | Yes | For C / C ++ |
| [Ruby on Rails](http://brakemanscanner.org/) | Yes | Only for Ruby on Rails |
| [VCG](http://sourceforge.net/projects/visualcodegrepp/) | Yes | GUI programs, simple rule matching |
| [BugScout](https://buguroo.com/products/bugblast-next-gen-appsec-platform/bugscout-sca) | No | Can not be flexibly expanded |
| [Contrast from Contrast Security](http://www.contrastsecurity.com/) | No | Can not be flexibly expanded|
| [IBM Security AppScan Source Edition](http://www-01.ibm.com/software/rational/products/appscan/source/) | No |Can not be flexibly expanded |
| [Insight](http://www.klocwork.com/products/insight.asp) | No | Can not be flexibly expanded|
| [Parasoft Test](http://www.parasoft.com/jsp/capabilities/static_analysis.jsp?itemId=547) | No | Can not be flexibly expanded |
| [Pitbull SCC](http://www.pitbullsoftware.net/pitbull-scc-en/) | No | Can not be flexibly expanded |
| [Seeker](http://www.quotium.com/prod/security.php) | No | Can not be flexibly expanded|
| [Pentest](http://www.sourcepatrol.co.uk/) | No | Can not be flexibly expanded|
| [CodeSecure Verifier](www.armorize.com) | No | Can not be flexibly expanded|
| [Coverity](http://www.coverity.com/products/security-advisor.html) | No | Can not be flexibly expanded |
| [PVS-Studio](http://www.viva64.com/en/) | No |Can not be flexibly expanded|
| [HP / Fortify](https://www.fortify.com/products/hpfssc/source-code-analyzer.html) | No | Can not be flexibly expanded |
| [Veracode](http://www.veracode.com/) | No | Can not be flexibly expanded

The focus of these projects are not the same, a very small number of commercial positioning in the enterprise code audit, but are closed-source.
Not an open source, and targeted at enterprise-level use.


As a business enterprise, we need:

- Can quickly scan for new vulnerabilities (Web applications every day there are new vulnerabilities / attack techniques appear to be able to quickly respond to the new vulnerability scanning)
- Ability to scan a variety of development languages (the company will develop a variety of languages, the need to support a variety of development language scanning)
- Ability to automatically scan, auto-report (manual participation to each project cost too much)

According to our comparison of research and found that no open-source scanner to meet our needs.
So we chose to do a set of enterprise-class white-box code audit system.

### How to do a code audit system?

Code audit in general can be divided into two types: static and dynamic,

#### 1. Static auditing

Through static analysis of source code, found in the source code of the logic, data processing, function used to identify the source code may be loopholes.

At the same time static analysis technology is also divided into several.

##### 1.1 Rule Matching

To put it bluntly is to scan the code in accordance with the specified rules of the problem.

For example, in the PHP Kohana framework, there is a uniform method to take a uniform parameter, and after security filtering. The possible situation is that the new R & D personnel are not familiar with the use of the PHP built-in ```$ _GET``` / ```$ _POST```, resulting in XSS, then you can use```$ _GET``` / ```$ _POST``` as a rule to find all the source code where these functions.

This approach is also a lot of white hat audit code used, although very straightforward, but the false positives will be more.

##### 1.2 Code Analysis

By analyzing the syntax of the code, the code execution flow is analyzed.

##### 1.3 Data flow analysis

By Fuzz input data, tracking data flow, to determine whether there is a risk.

#### 2. Dynamic auditing

By running the need to audit the code, tracking the flow of data to determine whether the system vulnerabilities.

We started out with only the types of vulnerabilities we were concerned about: high-risk files, high-risk functions, and regular Web vulnerabilities.
So our first version only static audit ** rule matching method **, on the issue of false positives in the actual scan we used a variety of ways to improve, to ensure that the false alarm rate of 5% or less.

### What should the company join the code audit?

#### 1. When the code is submitted

Code submitted to detect the problem is the most sensitive time, specifically through the hook svn or git commit to scan the submitted code.

Advantages: Timely

Disadvantages: affect the efficiency of submission

#### 2. After the code is submitted

By setting a regular task in the early hours of the regular code audit, the results through the mail or BUG system synchronization to the author.

Pros: Does not affect code submission

Disadvantages: the code may have been swept on the line before the problem

#### 3. When the code is released

Code before the release of the test environment to scan, on-line must have been scanned before and there is no high-risk vulnerabilities.

Advantages: no code has been swept on the line before the problem, to ensure that all on-line code has been scanned

Disadvantages: not found in time



Enterprises can access the ** code **, by setting the ** regular task scan ** to ensure timeliness and online code coverage.

Through our actual use of feelings, found that there are more usage:

#### 1. Used to determine the impact of new vulnerabilities

For example, to determine the impact of ImageMagick on all projects in the company, we can scan all company projects by setting scan rules to see which projects have invoked ImageMagick and are not available.

#### 2. Used to detect obvious code logic problems

Developers do not care to write == =, causing logic problems, and may even lead to security issues.

Or is a little less than the end of the semicolon, but the test did not cover it, resulting in an online 5xx.

These issues can also be discovered through code auditing.


There are other more use of skills, follow-up and then slowly add ...

---
### Application scenario

##### 1. Before the vulnerability (detection)
We will be common on the Internet vulnerabilities as a Cobra detection rules, can be found in the vulnerability before the white hat to scan out the risk point and resolve, preventive measures.

**example:**
Detecting high-risk files (.tar.gz / .rar / .bak / .swp) early in the code can prevent high-risk files from being downloaded.

##### 2. Vulnerability in the (scanning)
When the enterprise receives the white hat to submit the loophole, the enterprise will repair the loophole in the first time, and may through Cobra to add the scanning rule examination enterprise each item whether existence similar loophole.

**example:**
After the ImageMagick vulnerability, you can scan the history of all items through the Cobra scan rules to quickly scan, within minutes you will know dozens of projects which are useful to ImageMagick components, which there are loopholes, which can be immune.

##### 3. After the loopholes (restrictions)
When the enterprise fixes the vulnerability, you can set the repair / validation rules to restrict all future submission of the code need to repair / validation rules, or not on-line, reducing the possibility of the same loopholes reoccur.

### scanning method

Provides a self-service interface for scanning, and also provides a standard full-featured [API](http://cobra-docs.readthedocs.io/en/latest/API/) interface for third-party system calls (such as publishing systems)
![Cobra Framework](https://raw.githubusercontent.com/wufeifei/cobra/master/docs/FRAMEWORK.png)
![Cobra Manual](https://raw.githubusercontent.com/wufeifei/cobra/master/docs/MANUAL.png)

### Vulnerability type

In addition to common application vulnerabilities, including some code logic vulnerabilities and file permissions, sensitive files, etc.
See [Cobra Vulnerabilities](http://cobra-docs.readthedocs.io/en/latest/vulnerabilities/)

Scan file covers all common file types, registration detection rules support Java, PHP two languages.
See [Cobra Support Language](http://cobra-docs.readthedocs.io/en/latest/languages/)

In addition the accuracy of scanning, the scope of the rules are affected by the number of their impact.

### The scanning process

Scanner with multi-process design, multi-task can be done concurrent scanning, each scanning process will not be affected each other. Concurrent number of factors determined by the machine hardware can be quickly increased to expand concurrent scanning machine efficiency.
Scanner can scan the general items per second n million files (1 <n <10), scanning time is mainly affected by the number of rules triggered.

### Scan results

After each scan, the corresponding responsible person is informed and a scan report is generated. The report analyzes the code that presents the vulnerability and gives you a way to fix the vulnerability.
At the same time can be obtained through the Cobra API scan results, the release system can scan the results of the recommendations which decide whether to allow the release of this line.

### Validity of the rule

When the new rules are entered, you can test and verify the historical items first, and then when the false alarm rate decreases, the state of the rule is changed to online.
You can also for their own business, manually close some special rules.

### False positives
Rule validation results or there will be false positives, we can solve the problem of false positives in two ways.
1. Optimization rules - through the analysis of false positives to optimize the rules of detection logic
2. Whitelist - In some cases, we need a rule to release a line for a file (for example, eval ($ cmd) for some framework layers), you can use a whitelist