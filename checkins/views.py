from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Checkin, CheckinArquivo
from .serializers import (
    CheckinListSerializer, 
    CheckinDetailSerializer,
    CheckinCreateSerializer, 
    CheckinAvaliacaoSerializer,
    CheckinArquivoSerializer
)
from .permissions import IsMotorista, IsLogistica


class CheckinListView(generics.ListAPIView):
    """
    View para listar checkins
    """
    serializer_class = CheckinListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Se for da logística, vê todos os checkins
        if user.is_logistica():
            return Checkin.objects.all()
        
        # Se for motorista, vê apenas seus próprios checkins
        return Checkin.objects.filter(motorista=user)


class CheckinDetailView(generics.RetrieveAPIView):
    """
    View para detalhar um checkin específico
    """
    serializer_class = CheckinDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Se for da logística, vê todos os checkins
        if user.is_logistica():
            return Checkin.objects.all()
        
        # Se for motorista, vê apenas seus próprios checkins
        return Checkin.objects.filter(motorista=user)


class CheckinCreateView(APIView):
    """
    View para criar um novo checkin com arquivos
    """
    permission_classes = [IsAuthenticated, IsMotorista]
    parser_classes = (MultiPartParser, FormParser)
    
    @transaction.atomic
    def post(self, request, format=None):
        # Processa os dados do checkin
        checkin_serializer = CheckinCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not checkin_serializer.is_valid():
            return Response(checkin_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Cria o checkin
        checkin = checkin_serializer.save()
        
        # Processa os arquivos
        arquivos = request.FILES.getlist('arquivos')
        if not arquivos:
            return Response(
                {"arquivos": "É necessário enviar pelo menos um arquivo."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Salva cada arquivo associado ao checkin
        for arquivo in arquivos:
            CheckinArquivo.objects.create(
                checkin=checkin,
                arquivo=arquivo,
                nome_arquivo=arquivo.name
            )
        
        # Retorna o checkin criado com detalhes
        return Response(
            CheckinDetailSerializer(checkin).data,
            status=status.HTTP_201_CREATED
        )


class CheckinAprovarView(APIView):
    """
    View para aprovar um checkin
    """
    permission_classes = [IsAuthenticated, IsLogistica]
    
    def post(self, request, pk):
        checkin = get_object_or_404(Checkin, pk=pk)
        
        if checkin.status != 'pendente':
            return Response(
                {"erro": "Este checkin já foi avaliado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CheckinAvaliacaoSerializer(data=request.data)
        if serializer.is_valid():
            comentario = serializer.validated_data.get('comentario_avaliacao', '')
            checkin.aprovar(request.user, comentario)
            return Response(
                CheckinDetailSerializer(checkin).data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckinRejeitarView(APIView):
    """
    View para rejeitar um checkin
    """
    permission_classes = [IsAuthenticated, IsLogistica]
    
    def post(self, request, pk):
        checkin = get_object_or_404(Checkin, pk=pk)
        
        if checkin.status != 'pendente':
            return Response(
                {"erro": "Este checkin já foi avaliado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CheckinAvaliacaoSerializer(data=request.data)
        if serializer.is_valid():
            comentario = serializer.validated_data.get('comentario_avaliacao', '')
            checkin.rejeitar(request.user, comentario)
            return Response(
                CheckinDetailSerializer(checkin).data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckinPendentesView(generics.ListAPIView):
    """
    View para listar apenas checkins pendentes de aprovação
    """
    serializer_class = CheckinListSerializer
    permission_classes = [IsAuthenticated, IsLogistica]
    
    def get_queryset(self):
        return Checkin.objects.filter(status='pendente')


class CheckinArquivoUploadView(APIView):
    """
    View para adicionar mais arquivos a um checkin existente
    """
    permission_classes = [IsAuthenticated, IsMotorista]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, pk):
        checkin = get_object_or_404(Checkin, pk=pk, motorista=request.user)
        
        if checkin.status != 'pendente':
            return Response(
                {"erro": "Não é possível adicionar arquivos a um checkin já avaliado."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        arquivos = request.FILES.getlist('arquivos')
        if not arquivos:
            return Response(
                {"arquivos": "É necessário enviar pelo menos um arquivo."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        arquivos_salvos = []
        for arquivo in arquivos:
            arquivo_obj = CheckinArquivo.objects.create(
                checkin=checkin,
                arquivo=arquivo,
                nome_arquivo=arquivo.name
            )
            arquivos_salvos.append(arquivo_obj)
        
        return Response(
            CheckinArquivoSerializer(arquivos_salvos, many=True).data,
            status=status.HTTP_201_CREATED
        )