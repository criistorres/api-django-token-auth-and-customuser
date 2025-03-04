from django.db import models
from django.conf import settings
from django.utils import timezone


class Checkin(models.Model):
    """
    Modelo para registrar checkins de motoristas que precisam ser aprovados pela equipe de logística.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]
    
    motorista = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='checkins_enviados'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    comentario = models.TextField(blank=True)
    data_criacao = models.DateTimeField(default=timezone.now)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    # Preparado para incluir latitude e longitude no futuro
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Campos para rastreamento da aprovação/rejeição
    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='checkins_avaliados',
        null=True,
        blank=True
    )
    comentario_avaliacao = models.TextField(blank=True)
    data_avaliacao = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Checkin'
        verbose_name_plural = 'Checkins'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Checkin de {self.motorista.get_full_name()} - {self.get_status_display()}"
    
    def aprovar(self, avaliador, comentario=''):
        """
        Aprovar o checkin e registrar o avaliador
        """
        self.status = 'aprovado'
        self.aprovado_por = avaliador
        self.comentario_avaliacao = comentario
        self.data_avaliacao = timezone.now()
        self.save()
    
    def rejeitar(self, avaliador, comentario=''):
        """
        Rejeitar o checkin e registrar o avaliador
        """
        self.status = 'rejeitado'
        self.aprovado_por = avaliador
        self.comentario_avaliacao = comentario
        self.data_avaliacao = timezone.now()
        self.save()


class CheckinArquivo(models.Model):
    """
    Modelo para armazenar múltiplos arquivos associados a um checkin
    """
    checkin = models.ForeignKey(
        Checkin,
        on_delete=models.CASCADE,
        related_name='arquivos'
    )
    arquivo = models.FileField(upload_to='checkins/')
    nome_arquivo = models.CharField(max_length=255)
    data_upload = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Arquivo de Checkin'
        verbose_name_plural = 'Arquivos de Checkin'
    
    def __str__(self):
        return f"Arquivo {self.nome_arquivo} - Checkin {self.checkin.id}"