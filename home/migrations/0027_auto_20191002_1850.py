# Generated by Django 2.1.11 on 2019-10-02 18:50

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0026_auto_20191002_1626'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homepage',
            name='featured_incidents_label',
        ),
        migrations.AddField(
            model_name='homepage',
            name='featured_pages_label',
            field=models.CharField(default='Featured Articles', help_text='Title displayed above featured pages', max_length=255),
        ),
        migrations.AlterField(
            model_name='homepagefeature',
            name='home_page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='home.HomePage'),
        ),
    ]