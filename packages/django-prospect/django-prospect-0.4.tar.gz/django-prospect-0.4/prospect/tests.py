# -*- coding: utf-8 -*-

"""
This file makes tests to check if the Prospect application works well, using the unittest module. These tests will pass when you run "python manage.py test prospect".
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from prospect.models import Prospect, Field

class SimpleTest(TestCase):
    
    def setUp(self):
        self.field1 = Field.objects.create(name = u'communication')
        field2 = Field.objects.create(name = u'politics')
        field3 = Field.objects.create(name = u'research')
        field4 = Field.objects.create(name = u'education')
        self.prospect1 = Prospect.objects.create(
            company_name = u'société générale',
            field = self.field1,
            siret_code = u'55212022200013',
            title = u'm.',
            first_name = u'Frédéric',
            last_name = u'Oueda',
            profession = u'président du CA',
            e_mail = u'oueda@gmail.com',
            phone_number = u'0663532314',
            street = u'29 bd Haussmann',
            postal_code = u'75009',
            city = u'Paris',
        )
        self.prospect2 = Prospect.objects.create(
            company_name = u'EDF',
            field = field2,
            siret_code = u'55208131766522',
            title = u'mme.',
            first_name = u'Annie',
            last_name = u'Bobiba',
            profession = u'Secrétaire',
            e_mail = u'anibo@me.fr',
            phone_number = u'+35.1323152',
            street = u'23 rue de la Chandelle',
            postal_code = u'56002',
            city = u'Pitnif',
        )
        prospect3 = Prospect.objects.create(
            company_name = u'Comp',
            field = field3,
            siret_code = u'',
            title = u'',
            first_name = u'',
            last_name = u'',
            profession = u'',
            e_mail = u'',
            phone_number = u'',
            street = u'',
            postal_code = u'56224',
            city = u'London',
        )
        user = User.objects.create_superuser(u'admin', email=u'toto@toto.com', password=u'admin')
    
    def test_prospect_list(self):
        '''Test of the display of the list of prospects.'''
        url = reverse('prospect-list')
        self.client.login(username='admin', password='admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), Prospect.objects.count())
    
    def test_prospect_add(self):
        ''' Test of the insertion of a new prospect with all fields completed '''
        url = reverse('prospect-add')
        nb_prospect = Prospect.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'company_name' : u'FRANCE TELECOM',
            'field' : self.field1.id,
            'siret_code' : u'380 129 866 00014',
            'title' : u'Mme',
            'first_name' : u'ghislaine',
            'last_name' : u'coinaud',
            'profession' : u'administrateur',
            'e_mail' : u'Ghislaine@Laposte.Net',
            'phone_number' : u'0144442222',
            'street' : u'6 PL D ALLERAY',
            'postal_code' : u'75015',
            'city' : u'paris 15',
        })
        self.assertEqual(nb_prospect+1, Prospect.objects.count())
        # If the creation succeeded, the site must redirect (code 302) to the prospect list.
        self.assertEqual(response.status_code, 302)
        
    def test_prospect_wrong_siret_length(self):
        ''' Test of the insertion of a new prospect with a wrong length for the SIRET code '''
        url = reverse('prospect-add')
        nb_prospect = Prospect.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'company_name' : u'FRANCE TELECOM',
            'field' : self.field1.id,
            # We try to insert a SIRET code with 13 digits instead of 14.
            'siret_code' : u'380 129 866 0014',
            'title' : u'Mme',
            'first_name' : u'ghislaine',
            'last_name' : u'coinaud',
            'profession' : u'administrateur',
            'e_mail' : u'Ghislaine@Laposte.Net',
            'phone_number' : u'0144442222',
            'street' : u'6 PL D ALLERAY',
            'postal_code' : u'75015',
            'city' : u'paris 15',
        })
        # Check that nothing was added
        self.assertEqual(nb_prospect, Prospect.objects.count())
        # If the creation failed, we must stay on the same page.
        self.assertEqual(response.status_code, 200)
        
    def test_prospect_invalid_siret(self):
        ''' Test of the insertion of a new prospect with an invalid SIRET code '''
        url = reverse('prospect-add')
        nb_prospect = Prospect.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'company_name' : u'FRANCE TELECOM',
            'field' : self.field1.id,
            # We try to insert an invalid SIRET code.
            'siret_code' : u'380 129 866 00015',
            'title' : u'Mme',
            'first_name' : u'ghislaine',
            'last_name' : u'coinaud',
            'profession' : u'administrateur',
            'e_mail' : u'Ghislaine@Laposte.Net',
            'phone_number' : u'0144442222',
            'street' : u'6 PL D ALLERAY',
            'postal_code' : u'75015',
            'city' : u'paris 15',
        })
        # Check that nothing was added
        self.assertEqual(nb_prospect, Prospect.objects.count())
        # If the creation failed, we must stay on the same page.
        self.assertEqual(response.status_code, 200)
        
    def test_prospect_siret_with_letter(self):
        ''' Test of the insertion of a new prospect with a letter in the SIRET code '''
        url = reverse('prospect-add')
        nb_prospect = Prospect.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'company_name' : u'FRANCE TELECOM',
            'field' : self.field1.id,
            # We try to insert a SIRET code with a letter.
            'siret_code' : u'380 129 866 0001A',
            'title' : u'Mme',
            'first_name' : u'ghislaine',
            'last_name' : u'coinaud',
            'profession' : u'administrateur',
            'e_mail' : u'Ghislaine@Laposte.Net',
            'phone_number' : u'0144442222',
            'street' : u'6 PL D ALLERAY',
            'postal_code' : u'75015',
            'city' : u'paris 15',
        })
        # Check that nothing was added
        self.assertEqual(nb_prospect, Prospect.objects.count())
        # If the creation failed, we must stay on the same page.
        self.assertEqual(response.status_code, 200)
        
    def test_prospect_prefixed_phone(self):
        ''' Test of the insertion of a new prospect with a phone number with a prefix '''
        url = reverse('prospect-add')
        nb_prospect = Prospect.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'company_name' : u'FRANCE TELECOM',
            'field' : self.field1.id,
            'siret_code' : u'380 129 866 00014',
            'title' : u'Mme',
            'first_name' : u'ghislaine',
            'last_name' : u'coinaud',
            'profession' : u'administrateur',
            'e_mail' : u'Ghislaine@Laposte.Net',
            'phone_number' : u'+123.0144442222',
            'street' : u'6 PL D ALLERAY',
            'postal_code' : u'75015',
            'city' : u'paris 15',
        })
        self.assertEqual(nb_prospect+1, Prospect.objects.count())
        # If the creation succeeded, the site must redirect (code 302) to the prospect list.
        self.assertEqual(response.status_code, 302)
        
    def test_prospect_phone_with_letter(self):
        ''' Test of the insertion of a new prospect with a letter in the phone number '''
        url = reverse('prospect-add')
        nb_prospect = Prospect.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'company_name' : u'FRANCE TELECOM',
            'field' : self.field1.id,
            'siret_code' : u'380 129 866 00014',
            'title' : u'Mme',
            'first_name' : u'ghislaine',
            'last_name' : u'coinaud',
            'profession' : u'administrateur',
            'e_mail' : u'Ghislaine@Laposte.Net',
            # We try to insert a phone number with a letter.
            'phone_number' : u'01444A2222',
            'street' : u'6 PL D ALLERAY',
            'postal_code' : u'75015',
            'city' : u'paris 15',
        })
        # Check that nothing was added
        self.assertEqual(nb_prospect, Prospect.objects.count())
        # If the creation failed, we must stay on the same page.
        self.assertEqual(response.status_code, 200)
        
    def test_prospect_prefixed_phone_wrong_length(self):
        ''' Test of the insertion of a new prospect with a phone number with prefix, with a wrong number of digits '''
        url = reverse('prospect-add')
        nb_prospect = Prospect.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'company_name' : u'FRANCE TELECOM',
            'field' : self.field1.id,
            'siret_code' : u'380 129 866 00014',
            'title' : u'Mme',
            'first_name' : u'ghislaine',
            'last_name' : u'coinaud',
            'profession' : u'administrateur',
            'e_mail' : u'Ghislaine@Laposte.Net',
            # We try to insert a phone number with prefix, with not enough digits.
            'phone_number' : u'+33.38952063',
            'street' : u'6 PL D ALLERAY',
            'postal_code' : u'75015',
            'city' : u'paris 15',
        })
        # Check that nothing was added
        self.assertEqual(nb_prospect, Prospect.objects.count())
        # If the creation failed, we must stay on the same page.
        self.assertEqual(response.status_code, 200)
        
    def test_prospect_phone_wrong_length(self):
        ''' Test of the insertion of a new prospect with a phone number without prefix, with a wrong number of digits '''
        url = reverse('prospect-add')
        nb_prospect = Prospect.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'company_name' : u'FRANCE TELECOM',
            'field' : self.field1.id,
            'siret_code' : u'380 129 866 00014',
            'title' : u'Mme',
            'first_name' : u'ghislaine',
            'last_name' : u'coinaud',
            'profession' : u'administrateur',
            'e_mail' : u'Ghislaine@Laposte.Net',
            # We try to insert a phone number without prefix, with not enough digits.
            # As there is no phone prefix, we consider we are in France by default.
            'phone_number' : u'0 12 123 123',
            'street' : u'6 PL D ALLERAY',
            'postal_code' : u'75015',
            'city' : u'paris 15',
        })
        # Check that nothing was added
        self.assertEqual(nb_prospect, Prospect.objects.count())
        # If the creation failed, we must stay on the same page.
        self.assertEqual(response.status_code, 200)
        
    def test_prospect_phone_wrong_prefix_length(self):
        ''' Test of the insertion of a new prospect with a phone number with a wrong number of digits in the prefix '''
        url = reverse('prospect-add')
        nb_prospect = Prospect.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'company_name' : u'FRANCE TELECOM',
            'field' : self.field1.id,
            'siret_code' : u'380 129 866 00014',
            'title' : u'Mme',
            'first_name' : u'ghislaine',
            'last_name' : u'coinaud',
            'profession' : u'administrateur',
            'e_mail' : u'Ghislaine@Laposte.Net',
            # We try to insert a phone number with not enough digits in the prefix.
            'phone_number' : u'+3.389520634',
            'street' : u'6 PL D ALLERAY',
            'postal_code' : u'75015',
            'city' : u'paris 15',
        })
        # Check that nothing was added
        self.assertEqual(nb_prospect, Prospect.objects.count())
        # If the creation failed, we must stay on the same page.
        self.assertEqual(response.status_code, 200)
    
    def test_prospect_add_empty(self):
        ''' Test of the insertion of a new prospect with optional fields empty '''
        url = reverse('prospect-add')
        nb_prospect = Prospect.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'company_name' : u'FRANCE TELECOM',
            'field' : self.field1.id,
            'siret_code' : u'',
            'title' : u'',
            'first_name' : u'',
            'last_name' : u'',
            'profession' : u'',
            'e_mail' : u'',
            'phone_number' : u'',
            'street' : u'',
            'postal_code' : u'75015',
            'city' : u'paris 15',
        })
        self.assertEqual(nb_prospect+1, Prospect.objects.count())
        self.assertEqual(response.status_code, 302)
        
    def test_prospect_delete(self):
        ''' Test of the removal of a prospect '''
        prospect_id = self.prospect2.id
        url = reverse('prospect-delete', args=[prospect_id])
        nb_prospects = Prospect.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(nb_prospects-1, Prospect.objects.count())
        
        # You can't delete a prospect that's already been deleted.
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
    
    def test_prospect_detail(self):
        ''' Test of the display of the details of a prospect '''
        prospect_id = self.prospect1.id
        url = reverse('prospect-delete', args=[prospect_id])
        self.client.login(username='admin', password='admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_prospect_edit(self):
        ''' Test of the edition of a prospect '''
        prospect_id = self.prospect1.id
        url = reverse('prospect-edit', args=[prospect_id])
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'company_name' : u'FRANCE TELECOM',
            'field' : self.field1.id,
            'siret_code' : u'380 129 866 00014',
            'title' : u'Mme',
            'first_name' : u'ghislaine',
            'last_name' : u'coinaud',
            'profession' : u'administrateur',
            'e_mail' : u'Ghislaine@Laposte.Net',
            'phone_number' : u'0144442222',
            'street' : u'6 PL D ALLERAY',
            'postal_code' : u'75015',
            'city' : u'paris 15',
        })
        # If the modification succeeded, the site must redirect (code 302) to the prospect list.
        self.assertEqual(response.status_code, 302)

    #########################################################################################

    def test_field_list(self):
        '''Test of the display of the list of fields.'''
        url = reverse('field-list')
        self.client.login(username='admin', password='admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), Field.objects.count())
    
    def test_field_add(self):
        ''' Test of the insertion of a new field '''
        url = reverse('field-add')
        nb_field = Field.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'name' : u'arts',
        })
        self.assertEqual(nb_field+1, Field.objects.count())
        self.assertEqual(response.status_code, 302)
    
    def test_field_delete(self):
        ''' Test of the removal of a field '''
        field_id = self.field1.id
        url = reverse('field-delete', args=[field_id])
        nb_fields = Field.objects.count()
        self.client.login(username='admin', password='admin')
        response = self.client.post(url)
        self.assertEqual(nb_fields-1, Field.objects.count())
        self.assertEqual(response.status_code, 302)
        
        # You can't delete a field that's already been deleted.
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
    
    def test_field_detail(self):
        ''' Test of the display of the details of a field '''
        field_id = self.field1.id
        url = reverse('field-delete', args=[field_id])
        self.client.login(username='admin', password='admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_field_edit(self):
        ''' Test of the edition of a field '''
        field_id = self.field1.id
        url = reverse('field-edit', args=[field_id])
        self.client.login(username='admin', password='admin')
        response = self.client.post(url, {
            'name' : u'telecommunication',
        })
        # If the modification succeeded, the site must redirect (code 302) to the field list.
        self.assertEqual(response.status_code, 302)

