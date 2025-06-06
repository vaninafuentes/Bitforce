# Generated by Django 5.2 on 2025-04-23 00:05

import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AccountAdmin', '0003_alter_gymuser_branch'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gymuser',
            options={'verbose_name': 'gymuser', 'verbose_name_plural': 'gymusers'},
        ),
        migrations.AlterModelManagers(
            name='gymuser',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='gymuser',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined'),
        ),
        migrations.AddField(
            model_name='gymuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
        migrations.AddField(
            model_name='gymuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this gymuser belongs to. A gymuser will get all permissions granted to each of their groups.', related_name='gymuser_set', related_query_name='gymuser', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='gymuser',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this gymuser should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
        migrations.AddField(
            model_name='gymuser',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designates whether the gymuser can log into this admin site.', verbose_name='staff status'),
        ),
        migrations.AddField(
            model_name='gymuser',
            name='is_supergymuser',
            field=models.BooleanField(default=False, help_text='Designates that this gymuser has all permissions without explicitly assigning them.', verbose_name='supergymuser status'),
        ),
        migrations.AddField(
            model_name='gymuser',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='gymuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='last name'),
        ),
        migrations.AddField(
            model_name='gymuser',
            name='gymuser_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this gymuser.', related_name='gymuser_set', related_query_name='gymuser', to='auth.permission', verbose_name='gymuser permissions'),
        ),
        migrations.AddField(
            model_name='gymuser',
            name='gymusername',
            field=models.CharField(default=1, error_messages={'unique': 'A gymuser with that gymusername already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='gymusername'),
            preserve_default=False,
        ),
    ]
