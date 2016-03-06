# -*- coding: utf-8 -*-
""" ldap_target_ctl module used to add, delete, and update LDAP targets
"""

import emclpy
import xml.etree.ElementTree as ET
import sys
import os
import tempfile
import argparse
import getpass
import ConfigParser
import ast

__author__ = 'Tom Lester'
__email__ = 'tom.lester@oracle.com'
__version__ = '1.0.0'


def get_config():
    """ Searches for a config file.  If found, reads in the config and
        returns the configuration as a configParser object.  Search order
        is:  Current working directory -> User Home as .ldap_target_ctl.conf
             -> /etc/ldap_target_ctl -> the module directory (defaults)

        Inputs:
            None

        Returns:
            config - configParser object.
    """

    config_file_name = 'ldap_target_ctl.conf'
    # Look in current working directory for config file.
    if os.path.isfile(os.path.join(os.getcwd(), config_file_name)):
        config_file = os.path.join(os.getcwd(), config_file_name)

    # Look in user home dir
    elif os.path.isfile(os.path.join(os.path.expanduser('~'),
                                     '.{}'.format(config_file_name))):
        config_file = os.path.join(os.path.expanduser('~'),
                                   '.{}'.format(config_file_name))
    # Look in /etc/ldap_target_ctl
    elif os.path.isfile(os.path.join('/etc/ldap_target_ctl',
                                     config_file_name)):
        config_file = os.path.join('/etc/ldap_target_ctl', config_file_name)

    # Last... look for the default config in the module
    elif os.path.isfile(os.path.join(os.path.dirname(__file__),
                        config_file_name)):
        config_file = os.path.join(os.path.dirname(__file__), config_file_name)

    # Or fail
    else:
        print 'ERROR:  No acceptable {} file found!'.format(config_file_name)
        return 1

    config = ConfigParser.ConfigParser()
    config.read(config_file)

    # Return config.get(section, name)
    return config


def lifecycle_name():
    """ Define the key pair for validating lifecycle.  These are not in
        the config file as they are fixed values in OEM.

        Inputs:
            None

        Returns:
            Dictionary of lifecycle names
    """

    return {'none': 'None',
            'development': 'Developement',
            'test': 'Test',
            'staging': 'Stage',
            'production': 'Production',
            'mc': 'Mission Critical'
            }


def make_xml_template(ldap_user, ldap_password, ldap_host, ldap_port,
                      ldap_base, ldap_filter, ldap_search_attrib):
    """ Programatically builds the xml template used to build the
        generic service's tests and metric thresholds.

        Inputs:
            ldap_user - String, the ldap user for the test
            ldap_password - String, ldap user's password
            ldap_host - String, hostname of ldap host or vip
            ldap_port - String, port ldap is listening on
            ldap_base - String, direcotry structure where search resides
            ldap_filter - String, a filter to limit results
            ldap_search_attribute - String, search attribute to search for

        Returns:
            The root ojbect of type xml.etree.ElementTree.Element.  Use the
            etree functions to manipulate.
    """

    # Transaction properties for the LDAP_Test
    tx_properties = [{'name': 'ldap_attrvalue',
                      'string_value': ldap_search_attrib,
                      'prop_type': '1',
                      'encrypt': 'false'},
                     {'name': 'Collection Interval',
                      'num_value': '5.0',
                      'prop_type': '2',
                      'encrypt': 'false'},
                     {'name': 'connection',
                      'string_value': 'plain',
                      'prop_type': '1',
                      'encrypt': 'false'},
                     {'name': 'ldap_timeout',
                      'num_value': '60.0',
                      'prop_type': '2',
                      'encrypt': 'false'},
                     {'name': 'ldap_base',
                      'string_value': ldap_base,
                      'prop_type': '1',
                      'encrypt': 'false'},
                     {'name': 'ldap_port',
                      'num_value': ldap_port,
                      'prop_type': '2',
                      'encrypt': 'false'},
                     {'name': 'retryinterval',
                      'num_value': '5.0',
                      'prop_type': '2',
                      'encrypt': 'false'},
                     {'name': 'ldap_filter',
                      'string_value': ldap_filter,
                      'prop_type': '1',
                      'encrypt': 'false'},
                     {'name': 'ldap_attrname',
                      'string_value': 'uid',
                      'prop_type': '1',
                      'encrypt': 'false'},
                     {'name': 'numretries',
                      'num_value': '6.0',
                      'prop_type': '2',
                      'encrypt': 'false'},
                     {'name': 'ldap_user_name',
                      'string_value': ldap_user,
                      'prop_type': '1',
                      'encrypt': 'false'},
                     {'name': 'ldap_password',
                      'string_value': ldap_password,
                      'prop_type': '1',
                      'encrypt': 'true'},
                     {'name': 'ldap_address',
                      'string_value': ldap_host,
                      'prop_type': '1',
                      'encrypt': 'false'},
                     {'name': 'secure_auth',
                      'string_value': 'server',
                      'prop_type': '1',
                      'encrypt': 'false'}]

    # Response properties for LDAP_Test thresholds
    ldap_response_properties = [['AddressingSearch',
                                {'warning_threshold': '2000.0',
                                 'warning_operator': '0',
                                 'critical_threshold': '4000.0',
                                 'critical_operator': '0',
                                 'num_occurrences': '1'}],
                                ['BaseSearch',
                                {'warning_threshold': '2000.0',
                                 'warning_operator': '0',
                                 'critical_threshold': '4000.0',
                                 'critical_operator': '0',
                                 'num_occurrences': '1'}],
                                ['CompareOp',
                                {'warning_threshold': '2000.0',
                                 'warning_operator': '0',
                                 'critical_threshold': '4000.0',
                                 'critical_operator': '0',
                                 'num_occurrences': '1'}],
                                ['ConnectionTime',
                                {'warning_threshold': '2000.0',
                                 'warning_operator': '0',
                                 'critical_threshold': '4000.0',
                                 'critical_operator': '0',
                                 'num_occurrences': '1'}],
                                ['MessagingSearch',
                                {'warning_threshold': '2000.0',
                                 'warning_operator': '0',
                                 'critical_threshold': '4000.0',
                                 'critical_operator': '0',
                                 'num_occurrences': '1'}],
                                ['status',
                                {'warning_threshold': '0.0',
                                 'warning_operator': '1',
                                 'critical_threshold': '0.0',
                                 'critical_operator': '1',
                                 'num_occurrences': '1'}]]

    """ The section below builds the XML tree.
    """
    # Define root and basic structure
    root = ET.Element('transaction-template',
                      attrib={'template_type': 'generic_serivce',
                              'xmlns': 'template'})
    variables = ET.SubElement(root, 'variables')
    ET.SubElement(variables, 'variable', attrib={'name': 'PASSWORD1',
                                                 'value': 'XXXXXX'})
    transactions = ET.SubElement(root, 'transactions')
    mgmt_bcn_transaction = ET.SubElement(transactions, 'mgmt_bcn_transaction')
    mgmt_bcn_txn_with_props = ET.SubElement(mgmt_bcn_transaction,
                                            'mgmt_bcn_txn_with_props')
    ET.SubElement(mgmt_bcn_txn_with_props, 'mgmt_bcn_txn',
                  attrib={'is_representative': 'true', 'name': 'LDAP_test',
                          'monitoring': 'true', 'txn_type': 'LDAP'})
    properties = ET.SubElement(mgmt_bcn_txn_with_props, 'properties')

    # Itterate through the tx_properties to build tx_properties elements
    for element in tx_properties:
        ET.SubElement(properties, 'property', attrib=element)
    ET.SubElement(mgmt_bcn_transaction, 'steps_defn_with_props')
    ET.SubElement(mgmt_bcn_transaction, 'stepgroups_defn')
    txn_thresholds = ET.SubElement(mgmt_bcn_transaction, 'txn_thresholds')

    # Itterate through ldap_respons_properties to build tx_threshold elements
    for element in ldap_response_properties:
        mgmt_bcn_threshold = ET.SubElement(txn_thresholds,
                                           'mgmt_bcn_threshold',
                                           attrib=element[1])
        ET.SubElement(mgmt_bcn_threshold,
                      'mgmt_bcn_threshold_key',
                      attrib={'netric_name': 'ldap_response',
                              'metric_column': element[0]})
    ET.SubElement(mgmt_bcn_transaction, 'step_thresholds')
    ET.SubElement(mgmt_bcn_transaction, 'stepgroup_thresholds')
    # Return the XML root object
    return root


def get_arguments(args):
    """ Get arguments from input and checks if running in batch mode (-F)
        or interactive mode.   If "-F" is present, then it runs the first
        set of argument requirements.  If "-F" is not present, then it runs
        the second set of argument requirements.

        Inputs:
            args - list, List of arguments.  Typically supplied as a subset
                   of sys.argv from main().

        Returns:
            args - args namespace object.  See argsparse docs for more info.
                   input variables are callable by referencing the object
                   with variable name.
                        Example:  args = get_arguments(['-e', '11'])
                                  print args.entity_number
                                  >>> 11
    """

    beacons = ast.literal_eval(get_config().get('otes', 'beacons'))
    pod_help = ('The POD in which the URL check should originate.'
                'Options are: ') + ', '.join(beacons.keys())

    # Check to see if user is running batch mode and set appropriate inputs
    if '-F' in args:
        description = ('This program is used to provision LDAP (OID) targets '
                       'to be monitored by OEM.  Batch file is in the'
                       'following format (one line per target): '
                       'ldap_host:ldap_port:pod')
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('-F', '--batch_file',
                            help='Path to file with batch configuration file',
                            required=True)
        parser.add_argument('-U', '--ldap_user', help='LDAP User',
                            default=('cn=XXXXj,'
                                     'cn=Users,dc=us,dc=oracle,dc=com'))
        parser.add_argument('-w', '--ldap_password', help='LDAP User password',
                            default='XXXXXX')
        parser.add_argument('-B', '--ldap_base', help='LDAP Directory Base',
                            default=('cn=XXXXn,'
                                     'cn=Users,dc=us,dc=oracle,dc=com'))
        parser.add_argument('-f', '--ldap_filter', help='LDAP filter',
                            default='cn=XXXXXX')
        parser.add_argument('-a', '--ldap_search_attrib',
                            help='Search attribute for test',
                            default='Taleo_Obiee_Auth')
        parser.add_argument('-l', '--lifecycle',
                            help=('Lifecycle. Exmple: production, staging, '
                                  'test, development'), required=True)
        parser.add_argument('-e', '--entity_number',
                            help=('Two digit entity number.'
                                  'Example: 07, 05, 11'), required=True)
        parser.add_argument('-g', '--group',
                            help='Which OEM group to add target to',
                            default='OID')
        parser.add_argument('-L', '--em_login', help=('The OEM ID to run the '
                            'command as.'), required=True)
        return parser.parse_args(args)

    # If not in batch mode, get appropriate interactive inputs
    else:
        description = ('This program is used to provision LDAP (OID) targets '
                       'to be monitored by OEM.  Use "-F" to bulk load LDAP '
                       'targets from file. '
                       'Run "-h -F" to view help for batch')
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('-H', '--ldap_host', help='The FQDN LDAP Hostname',
                            required=True)
        parser.add_argument('-P', '--ldap_port', help='The LDAP server port',
                            required=True)
        parser.add_argument('-U', '--ldap_user', help='LDAP User',
                            default=('cn=XXXXX,'
                                     'cn=Users,dc=us,dc=oracle,dc=com'))
        parser.add_argument('-w', '--ldap_password', help='LDAP User password',
                            default='XXXXXX')
        parser.add_argument('-B', '--ldap_base', help='LDAP Directory Base',
                            default=('cn=XXXXXX,'
                                     'cn=Users,dc=us,dc=oracle,dc=com'))
        parser.add_argument('-f', '--ldap_filter', help='LDAP filter',
                            default='cn=XXXXX')
        parser.add_argument('-a', '--ldap_search_attrib',
                            help='Search attribute for test',
                            default='Taleo_Obiee_Auth')
        parser.add_argument('-l', '--lifecycle',
                            help=('Lifecycle. Exmple: production, staging, '
                                  'test, development'), default='production')
        parser.add_argument('-e', '--entity_number',
                            help=('Two digit entity number.'
                                  'Example: 07, 05, 11'), required=True)
        parser.add_argument('-p', '--pod', help=pod_help, required=True)
        parser.add_argument('-g', '--group',
                            help='Which OEM group to add target to',
                            default='OID')
        parser.add_argument('-L', '--em_login', help=('The OEM ID to run the '
                            'command as.'))
        return parser.parse_args(args)


def add_batch_ldap_targets(batch_file, ldap_user, ldap_password,
                           ldap_base, ldap_filter, ldap_search_attrib,
                           lifecycle, entity_number, group, em_user, em_pass):
    """ Recive arguments and create OEM LDAP targets from a batch file.

        Inputs:
            batch_file - String, Absolute path to batch file.
                         Batch file is formated as
                         follows (one line per serivce):

                                ldap_host:ldap_port:pod

            ldap_user - string, LDAP user
            ldap_password - string, ldap password
            ldap_base - string, ldap base
            ldap_filter - string, ldap search filter
            ldap_search_attrib - string, attribute to compare
            em_user - string, an authorized OEM user
            em_pass - string, oem password for said user

        Returns:
            code - int, error code.
    """

    url = get_config().get('oem', 'url')

    # Create the emcli client instance
    emcli = emclpy.Emclpy(url, em_user, em_pass)

    # Login to emcli and sync
    code, out, err = emcli.login()
    if code > 0:
        print err.strip()
        return code
    emcli.sync()

    # Read in batch file.
    batch = open(batch_file, 'r')

    # code_total keeps a running total of error codes while
    # batch adding targets
    code_total = 0

    # Itterate through the lines in the batch file
    for line in batch:
        ldap_host, ldap_port, pod = line.strip().split(':')

        # Look up and define which beacons to use for this POD
        beacons = ast.literal_eval(get_config().get('otes', 'beacons'))[pod]
        target_name = '{}_ldap'.format(ldap_host)
        entity_code = ast.literal_eval(get_config().get('otes', 'entities'))

        property_records = {'Department': entity_code[entity_number],
                            'Function': 'LDAP Service',
                            'Lifecycle Status': lifecycle,
                            'Pod': pod}

        root = make_xml_template(ldap_user, ldap_password, ldap_host,
                                 ldap_port, ldap_base, ldap_filter,
                                 ldap_search_attrib)

        xmlstr = ET.tostring(root)

        # Create temp file
        temp = tempfile.NamedTemporaryFile('w', 0)
        temp.write(xmlstr)  # Write XML temp file

        # Create LDAP Target
        code, out, err = emcli.create_generic_service(target_name,
                                                      temp.name,
                                                      beacons)
        if code > 0:
            print err.strip()
            code_total += code  # Add to error code count
        else:
            print out.strip()

        # Set target properties
        code, out, err = emcli.set_target_property_value(target_name,
                                                         'generic_service',
                                                         property_records)
        if code > 0:
            print err.strip()
            code_total += code  # Add to error code count
        else:
            print out.strip()

        # If the group variable is set, check to see if group exists.  If it
        # does, then add target to group.  If it doesn't, first create group,
        # then add to group.
        if group:
            if group in emcli.get_groups():
                code, out, err = emcli.add_to_group(group, target_name,
                                                    'generic_service')
                print out.strip()
            else:
                code, out, err = emcli.create_group(group)
                print out.strip()
                code, out, err = emcli.add_to_group(group, target_name,
                                                    'generic_service')
                print out.strip()

        temp.close()

    emcli.logout()  # Logout of EMCLI

    # Check error code totals and if greater than one, return error
    if code_total > 0:
        return 1
    else:
        return 0


def add_single_ldap_target(ldap_host, ldap_port, ldap_user, ldap_password,
                           ldap_base, ldap_filter, ldap_search_attrib, beacons,
                           lifecycle, entity_number, pod, group,
                           em_user, em_pass):
    """ Inputs:
            ldap_host - String, ldap hostname
            ldap_port - String, ldap port
            ldap_user - string, LDAP user
            ldap_password - string, ldap password
            ldap_base - string, ldap base
            ldap_filter - string, ldap search filter
            ldap_search_attrib - string, attribute to compare
            beacons - list, a list of beacon names know by OEM
            em_user - string, an authorized OEM user
            em_pass - string, oem password for said user

        Returns:
            code - int, error code.
    """

    entity_code = ast.literal_eval(get_config().get('otes', 'entities'))
    property_records = {'Department': entity_code[entity_number],
                        'Function': 'LDAP Service',
                        'Lifecycle Status': lifecycle,
                        'Pod': pod
                        }

    target_name = '{}_ldap'.format(ldap_host)
    root = make_xml_template(ldap_user, ldap_password, ldap_host,
                             ldap_port, ldap_base, ldap_filter,
                             ldap_search_attrib)

    # Build XML temp file
    xmlstr = ET.tostring(root)

    # Create temp file
    temp = tempfile.NamedTemporaryFile('w', 0)
    temp.write(xmlstr)  # Write xml to temp file.
    temp.close

    url = get_config().get('oem', 'url')

    # Crete emcli client object
    emcli = emclpy.Emclpy(url, em_user, em_pass)
    code, out, err = emcli.login()  # login to emcli
    if code > 0:
        print err.strip()
        return code
    emcli.sync()   # Sync with emcli

    # Create the LDAP target
    code, out, err = emcli.create_generic_service(target_name,
                                                  temp.name,
                                                  beacons)
    if code > 0:
        print err.strip()
        return code
    else:
        print out.strip()

    # Set target properties
    code, out, err = emcli.set_target_property_value(target_name,
                                                     'generic_service',
                                                     property_records)
    if code > 0:
        print err.strip()
        return code
    else:
        print out.strip()

    # If the group variable is set, check to see if group exists.  If it
    # does, then add target to group.  If it doesn't, first create group,
    # then add to group.
    if group:
        if group in emcli.get_groups():
            code, out, err = emcli.add_to_group(group, target_name,
                                                'generic_service')
            print out.strip()
        else:
            code, out, err = emcli.create_group(group)
            print out.strip()
            code, out, err = emcli.add_to_group(group, target_name,
                                                'generic_service')
            print out.strip()

    emcli.logout()  # Logout of emcli
    return code


def main():
    """ This is the main driver of the application.
    """

    args = get_arguments(sys.argv[1:])
    entity_code = ast.literal_eval(get_config().get('otes', 'entities'))

    # Validate lifecycle
    if str(args.lifecycle).lower() in lifecycle_name().keys():
        lifecycle = lifecycle_name()[str(args.lifecycle).lower()]
    else:
        print 'ERROR: {} is not a valid lifecycle'.format(args.lifecycle)
        return 1

    # Validate entity number
    if int(args.entity_number) in entity_code.keys():
        entity_number = int(args.entity_number)
    else:
        print ('ERROR: {} is not a valid OTES entity '
               'number').format(args.entity_number)
        return 1

    # Get user's OEM password
    em_pass = getpass.getpass('OEM Password for {}: '.format(args.em_login))

    # Get beacons list from config file
    beacons = ast.literal_eval(get_config().get('otes', 'beacons'))

    # If running in batch, drive in batch mode.
    if '-F' in sys.argv:
        args_list = [args.batch_file, args.ldap_user,
                     args.ldap_password, args.ldap_base, args.ldap_filter,
                     args.ldap_search_attrib, lifecycle,
                     entity_number, args.group, args.em_login, em_pass]
        return add_batch_ldap_targets(*args_list)
    # If not running in batch, drive in interactive mode
    else:
        args_list = [args.ldap_host, args.ldap_port, args.ldap_user,
                     args.ldap_password, args.ldap_base, args.ldap_filter,
                     args.ldap_search_attrib, beacons[args.pod],
                     lifecycle, entity_number, args.pod, args.group,
                     args.em_login, em_pass]
        return add_single_ldap_target(*args_list)


if __name__ == "__main__":
    sys.exit(main())
