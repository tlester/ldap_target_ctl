
# OID/LDAP Target Monitoring

OID is a generic LDAP service.  As such, OEM will monitor LDAP (OID) as a generic_service utilizing the LDAP service test type.  LDAP targets can be provisioned using OTES's ldap_target_ctl script.

## Prerequisites
- LDAP user created on each OID instance for the test to authenticate (see "Creating the Monitoring User" Installation Below):
- emclpy and ldap_target_ctl modules installed on a host that has access to the OEM servers (see "Software Installation" below.  NOTE.  Already installed on App Admin utility host "dcprutb06001")
- Java 1.6 or greater requires.   Set the $JAVA_HOME to a java that is 1.6 or greater, if needed.

## Usage
The ldap_target_ctl script should be executed from a utility host that has proper firewall access to the OEM host.  The script has already been installed on the App Admin utility host "dcprutb06001" where all pre-req's have been satisfied.  Many options have defaults, so only basic input is needed unless you have a special one off case.  See examples below for typical usage.

```
ldap_target_ctl -h
usage: ldap_target_ctl [-h] -H LDAP_HOST -P LDAP_PORT [-U LDAP_USER]
                       [-w LDAP_PASSWORD] [-B LDAP_BASE] [-f LDAP_FILTER]
                       [-a LDAP_SEARCH_ATTRIB] [-l LIFECYCLE] -e ENTITY_NUMBER
                       -p POD [-g GROUP] [-L EM_LOGIN]
This program is used to provision LDAP (OID) targets to be monitored by OEM.
Use "-F" to bulk load LDAP targets from file. Run "-h -F" to view help for
batch
optional arguments:
  -h, --help            show this help message and exit
  -H LDAP_HOST, --ldap_host LDAP_HOST
                        The FQDN LDAP Hostname
  -P LDAP_PORT, --ldap_port LDAP_PORT
                        The LDAP server port
  -U LDAP_USER, --ldap_user LDAP_USER
                        LDAP User
  -w LDAP_PASSWORD, --ldap_password LDAP_PASSWORD
                        LDAP User password
  -B LDAP_BASE, --ldap_base LDAP_BASE
                        LDAP Directory Base
  -f LDAP_FILTER, --ldap_filter LDAP_FILTER
                        LDAP filter
  -a LDAP_SEARCH_ATTRIB, --ldap_search_attrib LDAP_SEARCH_ATTRIB
                        Search attribute for test
  -l LIFECYCLE, --lifecycle LIFECYCLE
                        Lifecycle. Exmple: production, staging, test,
                        development
  -e ENTITY_NUMBER, --entity_number ENTITY_NUMBER
                        Two digit entity number.Example: 07, 05, 11
  -p POD, --pod POD     The POD in which the URL check should
                        originate.Options are: POD-U, POD-R, POD-Q, POD-P,
                        POD-G, POD-F, POD-E, POD-D, POD-C, POD-B, POD-A,
                        POD-N, POD-M, POD-K, POD-J
  -g GROUP, --group GROUP
                        Which OEM group to add target to
  -L EM_LOGIN, --em_login EM_LOGIN
                        The OEM ID to run the command as.
```
## Examples
### Single Target:
```
$ ldap_target_ctl -H some_ldap_host -P 1234 -p POD-B -e 11 -L tom.lester
OEM Password for tom.lester:
The specified service some_ldap_host_ldap/generic_service was created successfully.
Properties updated successfully
Group "OID:group" modified successfully
```

### Batch targets:
```
$ ldap_target_ctl -F /tmp/ldap_batch.txt -l production -e 11 -L sysman
```
In the case of a batch creation, the file supplied should be formatted with one line per target with hostname:port:POD.  Here's an example:
```
fake_ldap1:1234:POD-E
fake_ldap2:1234:POD-E
fake_ldap3:1234:POD-C
```

## Monitoring thresholds
In addition to availability status, which are event driven (i.e. target up or down), the following metrics for base search time are monitored.

|Comparison Operator|Warning Threshold|Critical Threshold|Collection Schedule| Occurrences|
|:-----:|:-----------:|:----------:|----------------|:------:|
|>      |2000m        |4000ms      |Every 2 minutes |    3   |

These thresholds are are set at the time of provisioning and can be altered on a per target bases.  Globally, they can be altered via the "LDAP_Template" under Enterprise -> Monitoring -> Monitoring Templates, then using emcli to apply_template.

## General Setup
The information below is really for info only.  This should already complete.
Config file
Config file search goes in the following order:
Current working directory as ldap_target_ctl.conf
User's home dir as ~/.ldap_target_ctl.conf
/etc/ldap_target_ctl.conf
The default ldap_target_ctl included in the ldap_target_ctl module (in Python's site-packages)

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
