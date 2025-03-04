from rest_framework import serializers
from .models import Checkin, CheckinArquivo
from django.contrib.auth import get_user_model

User = get_user_model()


class CheckinArquivoSerializer(serializers.ModelSerializer):
    """
    Serializer para arquivos de checkin
    """
    class Meta:
        model = CheckinArquivo
        fields = ('id', 'arquivo', 'nome_arquivo', 'data_upload')
        read_only_fields = ('data_upload',)


class CheckinListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar checkins com informações básicas
    """
    motorista_nome = serializers.SerializerMethodField()
    avaliador_nome = serializers.SerializerMethodField()
    qtd_arquivos = serializers.SerializerMethodField()
    
    class Meta:
        model = Checkin
        fields = ('id', 'motorista_nome', 'status', 'data_criacao', 
                  'avaliador_nome', 'data_avaliacao', 'qtd_arquivos')
    
    def get_motorista_nome(self, obj):
        return obj.motorista.get_full_name() or obj.motorista.email
    
    def get_avaliador_nome(self, obj):
        if obj.aprovado_por:
            return obj.aprovado_por.get_full_name() or obj.aprovado_por.email
        return None
    
    def get_qtd_arquivos(self, obj):
        return obj.arquivos.count()


class CheckinDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para visualização detalhada de um checkin
    """
    motorista_nome = serializers.SerializerMethodField()
    avaliador_nome = serializers.SerializerMethodField()
    arquivos = CheckinArquivoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Checkin
        fields = ('id', 'motorista', 'motorista_nome', 'status', 'comentario', 
                  'data_criacao', 'data_atualizacao', 'latitude', 'longitude',
                  'aprovado_por', 'avaliador_nome', 'comentario_avaliacao', 
                  'data_avaliacao', 'arquivos')
        read_only_fields = ('motorista', 'status', 'aprovado_por', 
                           'data_avaliacao', 'data_criacao', 'data_atualizacao')
    
    def get_motorista_nome(self, obj):
        return obj.motorista.get_full_name() or obj.motorista.email
    
    def get_avaliador_nome(self, obj):
        if obj.aprovado_por:
            return obj.aprovado_por.get_full_name() or obj.aprovado_por.email
        return None


class CheckinCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criar um novo checkin
    """
    class Meta:
        model = Checkin
        fields = ('comentario', 'latitude', 'longitude')
    
    def create(self, validated_data):
        # O motorista será o usuário autenticado
        validated_data['motorista'] = self.context['request'].user
        return super().create(validated_data)


class CheckinAvaliacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para aprovar ou rejeitar um checkin
    """
    class Meta:
        model = Checkin
        fields = ('comentario_avaliacao',)