[text](https://claude.ai/chat/90e53291-a83d-459b-88fc-1127f09034ca)
# Sistema de Rastreamento Logístico - Novo Fluxo

## Visão Geral

Este documento detalha o novo fluxo de trabalho para o Sistema de Rastreamento Logístico, que visa acompanhar todo o ciclo de entrega, desde a chegada do motorista ao Centro de Distribuição (CD) até a entrega final com canhoto assinado, permitindo inclusive a transferência de responsabilidade entre motoristas quando necessário.

## Conceitos-Chave

### Ordem de Transporte (OT)

Em vez de "Checkin", vamos renomear para "Ordem de Transporte" (OT), um conceito mais abrangente que representa todo o ciclo logístico de uma entrega, desde a retirada até a finalização.

### Fases da Ordem de Transporte

1. **Iniciada**: Motorista chega ao CD e registra sua chegada
2. **Em Carregamento**: Mercadoria sendo carregada, notas fiscais vinculadas
3. **Em Trânsito**: Mercadoria em rota para o destino
4. **Entregue**: Entrega finalizada com canhoto assinado
5. **Rejeitada/Cancelada**: Quando ocorrer algum problema que impeça a conclusão

## Alterações no Modelo de Dados

### Novo Modelo: OrdemTransporte (substitui o Checkin)

```python
class OrdemTransporte(models.Model):
    STATUS_CHOICES = [
        ('iniciada', 'Iniciada'),
        ('em_carregamento', 'Em Carregamento'),
        ('em_transito', 'Em Trânsito'),
        ('entregue', 'Entregue'),
        ('rejeitada', 'Rejeitada'),
    ]
    
    # Informações básicas
    numero_ot = models.CharField(max_length=30, unique=True)  # Gerado automaticamente
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='iniciada')
    
    # Motoristas
    motorista_retirada = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ots_retirada'
    )
    motorista_entrega = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ots_entrega',
        null=True, blank=True  # Pode ser o mesmo ou outro motorista
    )
    
    # Datas de tracking
    data_criacao = models.DateTimeField(default=timezone.now)
    data_carregamento = models.DateTimeField(null=True, blank=True)
    data_inicio_transito = models.DateTimeField(null=True, blank=True)
    data_entrega = models.DateTimeField(null=True, blank=True)
    
    # Localização
    local_retirada_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    local_retirada_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    local_entrega_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    local_entrega_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Comentários
    observacao_retirada = models.TextField(blank=True)
    observacao_entrega = models.TextField(blank=True)
    
    # Métodos
    def iniciar_carregamento(self):
        self.status = 'em_carregamento'
        self.data_carregamento = timezone.now()
        self.save()
    
    def iniciar_transito(self, motorista_entrega=None):
        self.status = 'em_transito'
        self.data_inicio_transito = timezone.now()
        if motorista_entrega:
            self.motorista_entrega = motorista_entrega
        else:
            self.motorista_entrega = self.motorista_retirada
        self.save()
    
    def finalizar_entrega(self, latitude=None, longitude=None, observacao=None):
        self.status = 'entregue'
        self.data_entrega = timezone.now()
        if latitude and longitude:
            self.local_entrega_lat = latitude
            self.local_entrega_lng = longitude
        if observacao:
            self.observacao_entrega = observacao
        self.save()
```

### Novo Modelo: NotaFiscal

```python
class NotaFiscal(models.Model):
    ordem_transporte = models.ForeignKey(
        OrdemTransporte, 
        on_delete=models.CASCADE,
        related_name='notas_fiscais'
    )
    numero = models.CharField(max_length=50)
    destinatario = models.CharField(max_length=200, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_emissao = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"NF {self.numero} - OT {self.ordem_transporte.numero_ot}"
```

### Modelo: Arquivo (adaptado do CheckinArquivo existente)

```python
class Arquivo(models.Model):
    TIPO_CHOICES = [
        ('foto_retirada', 'Foto na Retirada'),
        ('foto_entrega', 'Foto na Entrega'),
        ('canhoto', 'Canhoto Assinado'),
        ('documento', 'Documento Adicional'),
    ]
    
    ordem_transporte = models.ForeignKey(
        OrdemTransporte,
        on_delete=models.CASCADE,
        related_name='arquivos'
    )
    nota_fiscal = models.ForeignKey(
        NotaFiscal,
        on_delete=models.CASCADE,
        related_name='arquivos',
        null=True, blank=True  # Opcional, pois pode estar vinculado à OT sem NF específica
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    arquivo = models.FileField(upload_to='ots/')
    nome_arquivo = models.CharField(max_length=255)
    data_upload = models.DateTimeField(default=timezone.now)
    enviado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
```

## Endpoints da API

### 1. Criar Ordem de Transporte (Chegada ao CD)

```
POST /api/ots/criar/
```

Payload:
```json
{
  "observacao_retirada": "Chegando no CD para retirada",
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

### 2. Vincular Nota Fiscal à OT

```
POST /api/ots/{id_ot}/vincular-nota/
```

Payload:
```json
{
  "numero": "NFE-12345678",
  "destinatario": "Empresa XYZ Ltda",
  "valor": 1250.50,
  "data_emissao": "2025-03-06"
}
```

### 3. Atualizar Status da OT (Em Carregamento → Em Trânsito)

```
POST /api/ots/{id_ot}/iniciar-transito/
```

Payload:
```json
{
  "mesmo_motorista": true  // ou false se for outro motorista
}
```

### 4. Transferir OT para Outro Motorista

```
POST /api/ots/{id_ot}/transferir/
```

Payload:
```json
{
  "motorista_entrega_id": 123,
  "observacao": "Transferência devido à troca de turno"
}
```

### 5. Buscar OT por Número da Nota Fiscal

```
GET /api/ots/buscar-por-nota/{numero_nota}/
```

### 6. Finalizar Entrega (incluindo upload de canhotos)

```
POST /api/ots/{id_ot}/finalizar/
```

Payload (multipart/form-data):
```
observacao_entrega: "Entregue ao Sr. João na portaria"
latitude: -23.5505
longitude: -46.6333
canhotos: [arquivo1, arquivo2]
```

## Permissões e Regras de Negócio

1. **Motorista**:
   - Pode criar OTs
   - Pode vincular notas fiscais às OTs que criou
   - Pode atualizar status das OTs sob sua responsabilidade
   - Pode buscar OTs por número de nota fiscal
   - Pode transferir OTs para outros motoristas
   - Pode finalizar OTs sob sua responsabilidade

2. **Logística**:
   - Pode fazer tudo que o motorista faz
   - Pode vincular notas fiscais a qualquer OT
   - Pode transferir qualquer OT
   - Pode visualizar todas as OTs
   - Pode gerar relatórios e consultas avançadas

## Fluxo de Uso Detalhado

1. **Criação da OT**:
   - Motorista chega ao CD
   - Abre o aplicativo e registra sua chegada, criando uma OT
   - O sistema captura automaticamente a geolocalização
   - Um número de OT é gerado automaticamente

2. **Vinculação de Notas Fiscais**:
   - Durante o carregamento, o motorista ou equipe de logística escaneia/digita os números das notas fiscais
   - Cada nota fiscal é vinculada à OT
   - O status da OT é atualizado para "Em Carregamento"

3. **Início do Trânsito**:
   - Após o carregamento completo, o motorista confirma o início do trânsito
   - Se o mesmo motorista fará a entrega, ele mantém a responsabilidade
   - Caso contrário, pode transferir para outro motorista imediatamente ou posteriormente

4. **Transferência (quando aplicável)**:
   - Se outro motorista assumir a entrega, ele pode:
     - Receber a transferência diretamente do primeiro motorista
     - Buscar a OT pelo número da nota fiscal no app
   - Após confirmar a transferência, ele passa a ser o responsável pela entrega

5. **Finalização da Entrega**:
   - Na entrega, o motorista:
     - Registra a geolocalização
     - Adiciona observações sobre a entrega
     - Anexa fotos dos canhotos assinados
   - A OT é marcada como "Entregue"

## Casos de Uso Específicos

### Caso 1: Mesmo Motorista Faz Todo o Processo
1. Motorista chega ao CD e cria OT
2. Vincula notas fiscais e inicia o trânsito
3. Realiza a entrega e finaliza a OT com canhotos

### Caso 2: Troca de Motorista
1. Motorista A chega ao CD e cria OT
2. Vincula notas fiscais
3. Transfere para Motorista B (outro caminhão)
4. Motorista B aceita a transferência
5. Motorista B realiza a entrega e finaliza a OT com canhotos

### Caso 3: Busca por Nota Fiscal
1. Motorista A chega ao CD e cria OT
2. Vincula notas fiscais
3. Por alguma razão, não transfere formalmente via app
4. Motorista B precisa encontrar a OT
5. Busca pelo número da nota fiscal no app
6. Solicita transferência da OT para si
7. Realiza a entrega e finaliza

## Requisitos Técnicos para Implementação

1. **Back-end**:
   - Criar novos modelos (OrdemTransporte, NotaFiscal, Arquivo)
   - Implementar endpoints da API
   - Adaptar permissões (IsMotorista, IsLogistica)
   - Criar métodos para gerar número único de OT

2. **Front-end**:
   - Criar novas telas de fluxo:
     - Criação de OT
     - Vinculação de notas fiscais
     - Busca de OT por número de nota
     - Transferência de OT
     - Finalização com upload de canhotos
   - Implementar lógica para captura de geolocalização
   - Implementar scanner de código de barras/QR para notas fiscais (opcional)

## Considerações para Migração

- Manter tabelas antigas (Checkin) por um período para consulta histórica
- Criar script para migrar dados relevantes para o novo modelo
- Implementar período de transição onde ambos os fluxos funcionam paralelamente
- Treinar usuários no novo fluxo antes da transição completa

## Próximos Passos

1. Validar este fluxo com as equipes de motoristas e logística
2. Desenvolver protótipos de interface para testes com usuários
3. Implementar as alterações no banco de dados
4. Desenvolver os novos endpoints da API
5. Criar/adaptar a interface de usuário
6. Testar exaustivamente todos os casos de uso
7. Implementar em produção com período de transição
