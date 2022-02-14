# Generated by Django 3.2.12 on 2022-02-11 15:05

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0066_collection_management_permissions'),
        ('blog', '0021_alter_blogpage_body'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogIndexPageFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('blog_index_page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='featured_blogs', to='blog.blogindexpage')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.page')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]