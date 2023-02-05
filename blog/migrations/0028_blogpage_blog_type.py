# Generated by Django 3.2.16 on 2023-02-05 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0027_update_streamfields_to_use_json_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpage',
            name='blog_type',
            field=models.CharField(choices=[('default', 'Default Blog'), ('newsletter', 'Newsletter'), ('SPECIAL', 'Special Blog')], default='default', help_text='Select template used to display this post.', max_length=20),
        ),
    ]
