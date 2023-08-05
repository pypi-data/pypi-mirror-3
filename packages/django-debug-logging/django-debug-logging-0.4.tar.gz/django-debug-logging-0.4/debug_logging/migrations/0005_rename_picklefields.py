# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Rename the columns that will be converted to picklefields
        db.rename_column('debug_logging_debuglogrecord', 'settings_pickled', 'settings')
        db.rename_column('debug_logging_debuglogrecord', 'sql_queries_pickled', 'sql_queries')
        db.rename_column('debug_logging_debuglogrecord', 'cache_calls_pickled', 'cache_calls')


    def backwards(self, orm):
        # Rename the columns that were converted to picklefields
        db.rename_column('debug_logging_debuglogrecord', 'settings', 'settings_pickled')
        db.rename_column('debug_logging_debuglogrecord', 'sql_queries', 'sql_queries_pickled')
        db.rename_column('debug_logging_debuglogrecord', 'cache_calls', 'cache_calls_pickled')


    models = {
        'debug_logging.debuglogrecord': {
            'Meta': {'object_name': 'DebugLogRecord'},
            'cache_calls_pickled': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cache_deletes': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cache_get_many': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cache_gets': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cache_hits': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cache_misses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cache_num_calls': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cache_sets': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cache_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request_path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'settings_pickled': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sql_num_queries': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sql_queries_pickled': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sql_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'test_run': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['debug_logging.TestRun']"}),
            'timer_cputime': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'timer_ivcsw': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'timer_stime': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'timer_total': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'timer_utime': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'timer_vcsw': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'debug_logging.testrun': {
            'Meta': {'object_name': 'TestRun'},
            'avg_cache_hits': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'avg_cache_misses': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'avg_cpu_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'avg_sql_queries': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'avg_sql_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'avg_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_sql_queries': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'project_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'total_cache_hits': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_cache_misses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_cpu_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'total_sql_queries': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_sql_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'total_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['debug_logging']
