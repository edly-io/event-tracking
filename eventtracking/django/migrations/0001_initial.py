# Generated by Django 2.2.13 on 2020-07-26 09:33

from django.db import migrations, models
import django.utils.timezone
import eventtracking.django.models
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegExFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('backend_name', models.CharField(db_index=True, help_text='Name of the tracking backend on which this filter should be applied.<br/>Please note that this field is <b>case sensitive.</b>', max_length=50, verbose_name='Backend name')),
                ('is_enabled', models.BooleanField(default=True, verbose_name='Is Enabled')),
                ('filter_type', models.CharField(choices=[('blocklist', 'Blocklist'), ('allowlist', 'Allowlist')], help_text='Allowlist: Only events matching the regular expressions in the list will be allowed to passed through.<br/>Blocklist: Events matching any regular expression in the list will be blocked.', max_length=9, verbose_name='Filter type')),
                ('regular_expressions', models.TextField(help_text='This should be a list of regular expressions, seperated by a newline, for the events to be filtered.', max_length=500, validators=[eventtracking.django.models.validate_regex_list], verbose_name='List of regular expressions')),
            ],
            options={
                'verbose_name': 'Regular Expression Filter',
                'ordering': ('backend_name', 'is_enabled', '-modified'),
            },
        ),
    ]
