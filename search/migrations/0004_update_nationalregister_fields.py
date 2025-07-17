from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0003_nationalregister_address_line_1_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nationalregister',
            old_name='city',
            new_name='town',
        ),
        migrations.RenameField(
            model_name='nationalregister',
            old_name='state',
            new_name='parish',
        ),
        migrations.RenameField(
            model_name='nationalregister',
            old_name='postal_code',
            new_name='postcode',
        ),
        migrations.AddField(
            model_name='nationalregister',
            name='middle_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='nationalregister',
            name='sex',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='nationalregister',
            name='telephone_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='nationalregister',
            name='year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
