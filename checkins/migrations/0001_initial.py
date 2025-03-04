# Generated by Django 5.1.6 on 2025-03-03 16:16

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('aprovado', 'Aprovado'), ('rejeitado', 'Rejeitado')], default='pendente', max_length=10)),
                ('comentario', models.TextField(blank=True)),
                ('data_criacao', models.DateTimeField(default=django.utils.timezone.now)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('comentario_avaliacao', models.TextField(blank=True)),
                ('data_avaliacao', models.DateTimeField(blank=True, null=True)),
                ('aprovado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checkins_avaliados', to=settings.AUTH_USER_MODEL)),
                ('motorista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkins_enviados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Checkin',
                'verbose_name_plural': 'Checkins',
                'ordering': ['-data_criacao'],
            },
        ),
        migrations.CreateModel(
            name='CheckinArquivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arquivo', models.FileField(upload_to='checkins/')),
                ('nome_arquivo', models.CharField(max_length=255)),
                ('data_upload', models.DateTimeField(default=django.utils.timezone.now)),
                ('checkin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arquivos', to='checkins.checkin')),
            ],
            options={
                'verbose_name': 'Arquivo de Checkin',
                'verbose_name_plural': 'Arquivos de Checkin',
            },
        ),
    ]
