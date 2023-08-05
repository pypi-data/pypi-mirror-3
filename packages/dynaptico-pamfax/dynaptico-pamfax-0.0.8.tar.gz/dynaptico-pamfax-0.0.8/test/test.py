#!/usr/bin/env python

from pamfax import PamFax

import socket
import sys
import unittest
import time

sys.path = ['..:'] + sys.path

IP_ADDR = socket.gethostbyname('www.dynaptico.com')

MY_NUMBER = '+81345790510'
BASE_URI = 'sandbox-api.pamfax.biz'
USERNAME = 'username'
PASSWORD = 'password'
API_KEY = 'apikey'
API_SECRET = 'apisecret'
USERNAME = 'dynaptico'
PASSWORD = 'dyn4ptic0'
API_KEY = 'dynaptico'
API_SECRET = '8cvk25MP6w5aSf'
DROPBOX_USERNAME = 'dynaptico@gmail.com'
DROPBOX_PASSWORD = 'dyn4ptic0'

"""
Make sure to upload a file through

     https://sandbox-api.pamfax.biz/server/faxin/faxintest.php

before running this test.
"""

def _assert_json(message, response):
    print message
    print response
    assert response['result']['code'] == 'success'
    print '*'*10

def _assert_file(message, file, content_type):
    print message
    print content_type
    assert file is not None
    assert content_type is not None

# Seed our test account with credit and a fax
pamfax = PamFax(USERNAME, PASSWORD, base_uri=BASE_URI, api_key=API_KEY, api_secret=API_SECRET)

message = 'Adding credit to sandbox user'
response = pamfax.add_credit_to_sandbox_user(1000, "Testing purposes")
_assert_json(message, response)

message = 'Listing inbox faxes'
response = pamfax.list_inbox_faxes()
_assert_json(message, response)

files = response['InboxFaxes']['content']
file = files[0]
file_uuid = file['file_uuid']
uuid = file['uuid']

class TestPamFax(unittest.TestCase):
    """A set of unit tests for this implementation of the PamFax API."""
    
    @unittest.skip("demonstrating skipping")
    def test_Common(self):
        message = 'Getting current settings'
        response = pamfax.get_current_settings()
        _assert_json(message, response)
        
        message = 'Getting file'
        file, content_type = pamfax.get_file(file_uuid)
        _assert_file(message, file, content_type)
        
        message = 'Getting geo IP information'
        response = pamfax.get_geo_ip_information(IP_ADDR)
        _assert_json(message, response)
        
        message = 'Getting page preview'
        file, content_type = pamfax.get_page_preview(uuid, 1)
        _assert_file(message, file, content_type)
        
        message = 'Listing countries'
        response = pamfax.list_countries()
        _assert_json(message, response)
        
        message = 'Listing countries for zone'
        response = pamfax.list_countries_for_zone(1)
        _assert_json(message, response)
        
        message = 'Listing currencies 1'
        response = pamfax.list_currencies()
        _assert_json(message, response)
        
        message = 'Listing currencies 2'
        response = pamfax.list_currencies('JPY')
        _assert_json(message, response)
        
        message = 'Listing languages 1'
        response = pamfax.list_languages()
        _assert_json(message, response)
        
        message = 'Listing languages 2'
        response = pamfax.list_languages(50)
        _assert_json(message, response)
        
        message = 'Listing strings'
        response = pamfax.list_strings(['hello'])
        _assert_json(message, response)
        
        message = 'Listing supported file types'
        response = pamfax.list_supported_file_types()
        _assert_json(message, response)
        
        message = 'Listing timezones'
        response = pamfax.list_timezones()
        _assert_json(message, response)
        
        message = 'Listing versions'
        response = pamfax.list_versions()
        _assert_json(message, response)
        
        message = 'Listing zones'
        response = pamfax.list_zones()
        _assert_json(message, response)
    
    @unittest.skip("demonstrating skipping")
    def test_FaxHistory(self):
        message = 'Adding note to fax'
        response = pamfax.add_fax_note(uuid, 'This is my favorite fax')
        _assert_json(message, response)
        
        message = 'Counting faxes'
        response = pamfax.count_faxes('inbox')
        _assert_json(message, response)
        
        message = 'Deleting faxes'
        response = pamfax.delete_faxes([uuid])
        _assert_json(message, response)
        
        message = 'Restoring fax'
        response = pamfax.restore_fax(uuid)
        _assert_json(message, response)

        #message = 'Deleting faxes from trash'
        #response = pamfax.delete_faxes_from_trash([uuid])
        #_assert_json(message, response)
        
        message = 'Emptying trash'
        response = pamfax.empty_trash()
        _assert_json(message, response)
        
        message = 'Getting fax details'
        response = pamfax.get_fax_details(uuid)
        _assert_json(message, response)
        
        #message = 'Getting fax group'
        #response = pamfax.get_fax_group(uuid)
        #_assert_json(message, response)
        
        message = 'Getting inbox fax'
        response = pamfax.get_inbox_fax(uuid, mark_read=False)
        _assert_json(message, response)
        
        #message = 'Listing fax group'
        #response = pamfax.list_fax_group(uuid)
        #_assert_json(message, response)
        
        message = 'Listing fax notes'
        response = pamfax.list_fax_notes(uuid)
        _assert_json(message, response)
        
        message = 'Listing inbox faxes'
        response = pamfax.list_inbox_faxes()
        _assert_json(message, response)
        
        message = 'Listing outbox faxes'
        response = pamfax.list_outbox_faxes()
        _assert_json(message, response)
        
        message = 'Listing recent faxes'
        response = pamfax.list_recent_faxes()
        _assert_json(message, response)
        
        message = 'Listing sent faxes'
        response = pamfax.list_sent_faxes()
        _assert_json(message, response)
        
        out_uuid = response['SentFaxes']['content'][0]['uuid']
        
        message = 'Getting transmission report'
        file, content_type = pamfax.get_transmission_report(out_uuid)
        _assert_file(message, file, content_type)
        
        #message = 'Listing trash'
        #response = pamfax.list_trash()
        #_assert_json(message, response)
        
        message = 'Listing unpaid faxes'
        response = pamfax.list_unpaid_faxes()
        _assert_json(message, response)
        
        message = 'Setting fax as read'
        response = pamfax.set_fax_read(uuid)
        _assert_json(message, response)
        
        message = 'Setting faxes as read'
        response = pamfax.set_faxes_as_read([uuid])
        _assert_json(message, response)
        
        message = 'Setting spam state for faxes'
        response = pamfax.set_spam_state_for_faxes([uuid], is_spam=False)
        _assert_json(message, response)
    
    @unittest.skip("demonstrating skipping")
    def test_FaxJob(self):
        message = 'Creating a fax job'
        response = pamfax.create()
        _assert_json(message, response)
        
        message = 'Listing available covers'
        response = pamfax.list_available_covers()
        _assert_json(message, response)
        
        message = 'Adding a cover'
        response = pamfax.set_cover(response['Covers']['content'][1]['id'], 'Dynaptico: Tomorrow On Demand')
        _assert_json(message, response)
        
        message = 'Adding a remote file'
        response = pamfax.add_remote_file('https://s3.amazonaws.com/dynaptico/Dynaptico.pdf')
        _assert_json(message, response)
        
        message = 'Adding a local file'
        response = pamfax.add_file('Dynaptico.pdf')
        _assert_json(message, response)
        
        message = 'Removing a file'
        response = pamfax.remove_file(response['FaxContainerFile']['file_uuid'])
        _assert_json(message, response)
        
        message = 'Adding recipient 1'
        response = pamfax.add_recipient('+81345789554')
        _assert_json(message, response)
        
        message = 'Adding recipient 2'
        response = pamfax.add_recipient('+81362763902')
        _assert_json(message, response)
        
        message = 'Removing a recipient'
        response = pamfax.remove_recipient(response['FaxRecipient']['number'])
        _assert_json(message, response)
        
        message ='Listing recipients'
        response = pamfax.list_recipients()
        _assert_json(message, response)
        
        message = 'Listing fax files'
        response = pamfax.list_fax_files()
        _assert_json(message, response)
        
        # Check state
        print '*'*10
        print 'Checking state'
        t = 0
        while True:
            fax_state = pamfax.get_state()
            print fax_state
            if fax_state['FaxContainer']['state'] == 'ready_to_send':
                break
            time.sleep(2)
            t += 2
            print "%d seconds elapsed..." % t
        assert fax_state['FaxContainer']['state'] == 'ready_to_send'
        
        message = 'Preview the fax'
        response = pamfax.get_preview()
        _assert_json(message, response)
        
        message = 'Send the fax'
        response = pamfax.send()
        _assert_json(message, response)
        
        # This only works if you don't have enough credit now
        #message = 'Send the fax later'
        #response = pamfax.send_later()
        #_assert_json(message, response)
        
        # This only works after the fax has moved to the fax history
        #message = 'Cloning the fax'
        #response = pamfax.clone_fax(faxjob['FaxContainer']['uuid'])
        #_assert_json(message, response)
    
    @unittest.skip("demonstrating skipping")
    def test_NumberInfo(self):
        message = 'Getting number info'
        response = pamfax.get_number_info('+81362763902')
        _assert_json(message, response)
        
        message = 'Getting page price'
        response = pamfax.get_page_price('+81362763902')
        _assert_json(message, response)
    
    @unittest.skip("demonstrating skipping")
    def test_OnlineStorage(self):
        message = 'Dropping authentication'
        response = pamfax.drop_authentication('DropBoxStorage')
        _assert_json(message, response)
        
        message = 'Authenticating'
        response = pamfax.authenticate('DropBoxStorage', DROPBOX_USERNAME, DROPBOX_PASSWORD)
        _assert_json(message, response)
        
        message = 'Getting provider logo'
        file, content_type = pamfax.get_provider_logo('DropBoxStorage', 16)
        _assert_file(message, file, content_type)
        
        message = 'Listing folder contents'
        response = pamfax.list_folder_contents('DropBoxStorage')
        _assert_json(message, response)
        
        message = 'Listing providers'
        response = pamfax.list_providers()
        _assert_json(message, response)
        
        #message = 'Setting auth token'
        #response = pamfax.set_auth_token('DropBoxStorage', token)
        #_assert_json(message, response)
    
    def test_Session(self):
        #message = 'Creating login identifier'
        #response = pamfax.create_login_identifier(timetolifeminutes=10)
        #_assert_json(message, response)
        
        #message = 'Listing changes'
        #response = pamfax.list_changes()
        #_assert_json(message, response)
        
        #message = 'Logging out'
        #response = pamfax.logout()
        #_assert_json(message, response)
        
        message = 'Pinging'
        response = pamfax.ping()
        _assert_json(message, response)
        
        #message = 'Registering listener'
        #response = pamfax.register_listener('faxsending')
        #_assert_json(message, response)
        
        #message = 'Reloading user'
        #response = pamfax.reload_user()
        #_assert_json(message, response)
        
        #message = 'Verifying user'
        #response = pamfax.verify_user(USERNAME, PASSWORD)
        #_assert_json(message, response)
#
#    def test_Shopping(self):
#    def get_invoice(self, payment_uuid, hidecopy=None):
#    def get_nearest_fax_in_number(self, ip_address):
#    def get_shop_link(self, type=None, product=None, pay=None):
#    def list_available_items(self):
#    def list_fax_in_areacodes(self, country_code, state=None):
#    def list_fax_in_countries(self):
#    def redeem_credit_voucher(self, vouchercode):
#
#    def test_UserInfo(self):
#    def create_user(self, name, username, password, email, culture, externalprofile=None, campaign_id=None):
#    def delete_user(self):
#    def get_culture_info(self):
#    def get_users_avatar(self, provider=None):
#    def has_avatar(self):
#    def has_plan(self):
#    def list_expirations(self, type=None):
#    def list_inboxes(self, expired_too=None, shared_too=None):
#    def list_orders(self, current_page=None, items_per_page=None):
#    def list_profiles(self):
#    def list_user_agents(self, max=None):
#    def list_wall_messages(self, count=None, data_to_list=None):
#    def save_user(self, user=None, profile=None):
#    def send_message(self, body, type=None, recipient=None, subject=None):
#    def send_password_reset_message(self, username, user_ip=None):
#    def set_online_storage_settings(self, provider, settings):
#    def set_password(self, password, hashFunction=None):
#    def set_profile_properties(self, profile, properties, ignoreerrors=None):
#    def validate_new_username(self, username, dictionary=None):

if __name__ == '__main__':
    unittest.main()
