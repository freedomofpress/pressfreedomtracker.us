# Generated by Django 3.2.12 on 2022-03-22 20:41

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0088_auto_20220315_1539'),
        ('home', '0036_categories_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataVizTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('home_page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_viz_tags', to='home.homepage')),
                ('tag', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, to='common.commontag')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
