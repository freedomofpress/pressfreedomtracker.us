# Generated by Django 2.0.13 on 2019-03-18 20:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0021_auto_20180215_0208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='search_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='common.CustomImage', verbose_name='Search image'),
        ),
    ]