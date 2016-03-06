#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
test_ldap_target_ctl
----------------------------------

Tests for `ldap_target_ctl` module.
"""

import unittest
import ldap_target_ctl
import emclpy
import time


LDAP_USER = 'cn=otes_oem_auth,cn=Users,dc=us,dc=oracle,dc=com'
LDAP_PASSWORD = 'taleo123'
LDAP_HOST = 'dcppidb05011.techno.taleocloud.net'
LDAP_PORT = '3060'
LDAP_BASE = 'cn=otes_oem_auth,cn=Users,dc=us,dc=oracle,dc=com'
LDAP_FILTER = 'cn=otes_oem_auth'
LDAP_SEARCH_ATTRIB = 'Taleo_Obiee_Auth'
POD = 'POD-J'
EM_USER = 'sysman'
EM_PASS = 'welcome1'
BEACONS = ['chprmoj11001.tee.taleocloud.net_beacon']
LIFECYCLE = 'Production'
ENTITY_NUMBER = 11
GROUP = 'OID'


# Environments for testing.
# Set url appropriately before running tests.
testing_environment = {'dev': 'https://localhost:7799/em',
                       'pp': '',
                       'prod': ''
                       }
url = testing_environment['dev']
username = 'sysman'
password = 'welcome1'


class TestLdap_target_ctl(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_make_xml_template(self):
        root = ldap_target_ctl.make_xml_template(LDAP_USER, LDAP_PASSWORD,
                                                 LDAP_HOST, LDAP_PORT,
                                                 LDAP_BASE, LDAP_FILTER,
                                                 LDAP_SEARCH_ATTRIB)
        self.assertEqual(root.keys()[1], 'xmlns')

    def test_get_arguments(self):
        input_args = ['-F', '/tmp/test.tl', '-l', 'production',
                      '-e', '11', '-L', 'tom.lester']
        args = ldap_target_ctl.get_arguments(input_args)
        self.assertEqual(args.lifecycle, 'production')
        input_args = ['-H', '0.0.0.0', '-P', '3060', '-l', 'production',
                      '-e', '11', '-p', 'POD-E', '-L', 'tom.lester']
        args = ldap_target_ctl.get_arguments(input_args)
        self.assertEqual(args.pod, 'POD-E')

    def test_add_single_ldap_target(self):
        args = [LDAP_HOST, LDAP_PORT, LDAP_USER, LDAP_PASSWORD, LDAP_BASE,
                LDAP_FILTER, LDAP_SEARCH_ATTRIB, BEACONS, LIFECYCLE,
                ENTITY_NUMBER, POD, GROUP, EM_USER, EM_PASS]
        code = ldap_target_ctl.add_single_ldap_target(*args)
        self.assertEqual(code, 0)
        emcli = emclpy.Emclpy(url, username, password)
        emcli.login()
        emcli.sync()
        time.sleep(10)
        code, out, err = emcli.delete_target('{}_ldap'.format(LDAP_HOST),
                                             'generic_service')
        self.assertEqual(code, 0)

    def test_add_batch_ldap_targets(self):
        batch_file = '/tmp/ldap_batch.txt'
        batch = open(batch_file, 'w+r', 0)
        batch.write('fake_ldap1:3060:POD-E\n')
        batch.write('fake_ldap2:3060:POD-E\n')
        batch.write('fake_ldap3:3060:POD-E\n')
        batch.seek(0)
        args = [batch_file, LDAP_USER, LDAP_PASSWORD, LDAP_BASE,
                LDAP_FILTER, LDAP_SEARCH_ATTRIB, LIFECYCLE, ENTITY_NUMBER,
                GROUP, EM_USER, EM_PASS]
        code = ldap_target_ctl.add_batch_ldap_targets(*args)
        self.assertEqual(code, 0)
        emcli = emclpy.Emclpy(url, username, password)
        emcli.login()
        emcli.sync()
        time.sleep(10)
        for line in batch:
            host = line.strip().split(':')[0]
            code, out, err = emcli.delete_target('{}_ldap'.format(host),
                                                 'generic_service')
            self.assertEqual(code, 0)
        batch.close()


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
