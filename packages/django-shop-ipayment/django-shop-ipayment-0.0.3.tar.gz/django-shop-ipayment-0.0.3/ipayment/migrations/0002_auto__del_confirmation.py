# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Confirmation'
        db.delete_table('ipayment_confirmation')


    def backwards(self, orm):
        
        # Adding model 'Confirmation'
        db.create_table('ipayment_confirmation', (
            ('trxuser_id', self.gf('django.db.models.fields.IntegerField')()),
            ('ret_booknr', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('ret_transdatetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('trx_paymenttyp', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('ret_trx_number', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('ret_errorcode', self.gf('django.db.models.fields.IntegerField')()),
            ('trx_typ', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('addr_name', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('trx_currency', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('trx_amount', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
            ('ret_status', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('ret_authcode', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('trx_paymentmethod', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('shopper_id', self.gf('django.db.models.fields.IntegerField')()),
            ('trx_remoteip_country', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ret_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
        ))
        db.send_create_signal('ipayment', ['Confirmation'])


    models = {
        
    }

    complete_apps = ['ipayment']
