# Generated by Django 4.2 on 2024-07-03 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_alter_category_parent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='file',
            old_name='parent',
            new_name='product',
        ),
        migrations.AddField(
            model_name='file',
            name='file_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'audio'), (2, 'video'), (3, 'pdf')], default=2, verbose_name='file type'),
            preserve_default=False,
        ),
    ]