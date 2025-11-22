# 🚀 Ejemplos de Uso - Sistema NFT Refactorizado

## 📋 Índice
1. [Flujo Completo de un Servicio](#flujo-completo)
2. [Endpoints de Gestión](#endpoints-gestion)
3. [Endpoints de Estadísticas](#endpoints-estadisticas)
4. [Casos de Uso Comunes](#casos-uso)
5. [Respuestas de Error](#respuestas-error)

---

## 🔄 Flujo Completo de un Servicio {#flujo-completo}

### Paso 1: Crear un Servicio
**Request:**
```bash
curl -X POST "http://localhost:8000/servicios/crear" \
  -H "Content-Type: application/json" \
  -d '{
    "destinatario": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb6"
  }'
```

**Response:**
```json
{
  "success": true,
  "tokenId": 1,
  "destinatario": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb6",
  "estado": 1,
  "estadoNombre": "CREADO",
  "transaction": {
    "transactionHash": "0xabc123...",
    "blockNumber": 217648900,
    "gasUsed": 85000,
    "status": 1
  }
}
```

### Paso 2: Asignar Acompañante (Transfiere NFT)
**Request:**
```bash
curl -X POST "http://localhost:8000/servicios/1/asignar-acompanante" \
  -H "Content-Type: application/json" \
  -d '{
    "acompanante": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"
  }'
```

**Response:**
```json
{
  "success": true,
  "tokenId": 1,
  "acompanante": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4",
  "nuevoEstado": 2,
  "estadoNombre": "ENCONTRADO",
  "nftTransferido": true,
  "transaction": {
    "transactionHash": "0xdef456...",
    "blockNumber": 217648950,
    "gasUsed": 95000,
    "status": 1
  }
}
```

**⚠️ Importante:** El NFT ahora pertenece al acompañante

### Paso 3: Finalizar Servicio
**Request:**
```bash
curl -X POST "http://localhost:8000/servicios/1/cambiar-estado" \
  -H "Content-Type: application/json" \
  -d '{
    "nuevoEstado": 3
  }'
```

**Response:**
```json
{
  "success": true,
  "tokenId": 1,
  "estadoAnterior": 2,
  "nuevoEstado": 3,
  "estadoNombre": "FINALIZADO",
  "transaction": {
    "transactionHash": "0xghi789...",
    "blockNumber": 217649000,
    "gasUsed": 45000,
    "status": 1
  }
}
```

---

## 📝 Endpoints de Gestión {#endpoints-gestion}

### POST /servicios/crear
Crea un nuevo servicio NFT en estado CREADO.

**Request Body:**
```json
{
  "destinatario": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb6"
}
```

**Response:**
```json
{
  "success": true,
  "tokenId": 2,
  "destinatario": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb6",
  "estado": 1,
  "estadoNombre": "CREADO",
  "transaction": {...}
}
```

### POST /servicios/{tokenId}/asignar-acompanante
Asigna un acompañante y transfiere el NFT automáticamente.

**Request Body:**
```json
{
  "acompanante": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"
}
```

**Response:**
```json
{
  "success": true,
  "tokenId": 2,
  "acompanante": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4",
  "nuevoEstado": 2,
  "estadoNombre": "ENCONTRADO",
  "nftTransferido": true,
  "transaction": {...}
}
```

### POST /servicios/{tokenId}/cambiar-estado
Cambia el estado de un servicio (principalmente para finalizar).

**Request Body:**
```json
{
  "nuevoEstado": 3
}
```

**Estados válidos:**
- `1` = CREADO
- `2` = ENCONTRADO
- `3` = FINALIZADO

### GET /servicios/{tokenId}/estado
Consulta el estado actual de un servicio.

**Request:**
```bash
curl "http://localhost:8000/servicios/1/estado"
```

**Response:**
```json
{
  "tokenId": 1,
  "estado": 3,
  "estadoNombre": "FINALIZADO"
}
```

### GET /servicios/{tokenId}/acompanante
Obtiene el acompañante asignado a un servicio.

**Request:**
```bash
curl "http://localhost:8000/servicios/1/acompanante"
```

**Response:**
```json
{
  "tokenId": 1,
  "acompanante": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"
}
```

---

## 📊 Endpoints de Estadísticas {#endpoints-estadisticas}

### GET /estadisticas/{wallet}
Obtiene estadísticas completas de una wallet específica.

**Request:**
```bash
curl "http://localhost:8000/estadisticas/0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"
```

**Response:**
```json
{
  "wallet": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4",
  "estadisticas": {
    "totalServicios": 5,
    "serviciosCreados": 1,
    "serviciosEncontrados": 2,
    "serviciosFinalizados": 2,
    "porcentajeCompletado": 40.0
  },
  "servicios": [
    {
      "tokenId": 1,
      "estado": 3,
      "estadoNombre": "FINALIZADO",
      "acompanante": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"
    },
    {
      "tokenId": 3,
      "estado": 2,
      "estadoNombre": "ENCONTRADO",
      "acompanante": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"
    },
    {
      "tokenId": 5,
      "estado": 2,
      "estadoNombre": "ENCONTRADO",
      "acompanante": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"
    },
    {
      "tokenId": 7,
      "estado": 3,
      "estadoNombre": "FINALIZADO",
      "acompanante": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"
    },
    {
      "tokenId": 9,
      "estado": 1,
      "estadoNombre": "CREADO",
      "acompanante": null
    }
  ],
  "resumen": {
    "serviciosActivos": 3,
    "serviciosCompletados": 2,
    "tieneServiciosEnProceso": true
  }
}
```

### GET /estadisticas/general/resumen
Obtiene un resumen general del sistema completo.

**Request:**
```bash
curl "http://localhost:8000/estadisticas/general/resumen"
```

**Response:**
```json
{
  "totalNFTsCreados": 10,
  "estadisticasPorEstado": {
    "creados": 2,
    "encontrados": 5,
    "finalizados": 3
  },
  "tasaFinalizacion": 30.0,
  "resumen": {
    "serviciosActivos": 7,
    "serviciosCompletados": 3,
    "tasaAsignacion": 80.0
  }
}
```

---

## 💡 Casos de Uso Comunes {#casos-uso}

### Caso 1: Cliente solicita múltiples servicios
```bash
# Crear 3 servicios para el mismo cliente
for i in {1..3}; do
  curl -X POST "http://localhost:8000/servicios/crear" \
    -H "Content-Type: application/json" \
    -d '{
      "destinatario": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb6"
    }'
done

# Verificar servicios creados
curl "http://localhost:8000/estadisticas/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb6"
```

### Caso 2: Acompañante consulta sus servicios asignados
```bash
# Un acompañante quiere ver todos sus servicios
curl "http://localhost:8000/estadisticas/0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"

# La respuesta incluirá solo los NFTs que posee (servicios asignados)
```

### Caso 3: Dashboard administrativo
```bash
# Obtener resumen general del sistema
curl "http://localhost:8000/estadisticas/general/resumen"

# Obtener información del contrato
curl "http://localhost:8000/info/contrato"

# Verificar salud del sistema
curl "http://localhost:8000/health"
```

### Caso 4: Flujo rápido de servicio
```python
import requests
import json

BASE_URL = "http://localhost:8000"
cliente = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb6"
acompanante = "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"

# 1. Crear servicio
response = requests.post(
    f"{BASE_URL}/servicios/crear",
    json={"destinatario": cliente}
)
servicio = response.json()
token_id = servicio["tokenId"]

# 2. Asignar acompañante (transfiere NFT)
response = requests.post(
    f"{BASE_URL}/servicios/{token_id}/asignar-acompanante",
    json={"acompanante": acompanante}
)

# 3. Finalizar servicio
response = requests.post(
    f"{BASE_URL}/servicios/{token_id}/cambiar-estado",
    json={"nuevoEstado": 3}
)

# 4. Ver estadísticas del acompañante
response = requests.get(f"{BASE_URL}/estadisticas/{acompanante}")
stats = response.json()
print(f"Servicios completados: {stats['estadisticas']['serviciosFinalizados']}")
```

---

## ❌ Respuestas de Error {#respuestas-error}

### Error: Servicio no existe
```json
{
  "detail": "Servicio no existe"
}
```

### Error: Estado inválido
```json
{
  "detail": "Estado debe ser 1, 2 o 3"
}
```

### Error: Transición no permitida
```json
{
  "detail": "Servicio debe estar en ENCONTRADO"
}
```

### Error: Acompañante no asignado
```json
{
  "detail": "Acompanante no asignado"
}
```

### Error: Dirección inválida
```json
{
  "detail": "Invalid address format"
}
```

### Error: Sin fondos para gas
```json
{
  "detail": "insufficient funds for gas * price + value"
}
```

---

## 🔍 Consultas Útiles

### Verificar propietario actual de un NFT
```bash
# Antes de asignar acompañante
curl "http://localhost:8000/servicios/1/estado"
# El NFT pertenece al cliente

# Después de asignar acompañante
curl "http://localhost:8000/estadisticas/0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"
# El NFT ahora pertenece al acompañante
```

### Monitorear progreso de servicios
```bash
# Ver todos los servicios y sus estados
curl "http://localhost:8000/estadisticas/general/resumen"

# Ver logs de transacciones
curl "http://localhost:8000/logs/transacciones?limit=10"

# Ver estadísticas de uso
curl "http://localhost:8000/logs/estadisticas"
```

### Configurar URIs para estados
```bash
# Configurar URI para estado CREADO
curl -X POST "http://localhost:8000/configuracion/uri-estado" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": 1,
    "nuevaURI": "ipfs://QmCreado123..."
  }'

# Configurar URI para estado ENCONTRADO
curl -X POST "http://localhost:8000/configuracion/uri-estado" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": 2,
    "nuevaURI": "ipfs://QmEncontrado456..."
  }'

# Configurar URI para estado FINALIZADO
curl -X POST "http://localhost:8000/configuracion/uri-estado" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": 3,
    "nuevaURI": "ipfs://QmFinalizado789..."
  }'
```

---

## 📈 Métricas y KPIs

### Para el Cliente
- Total de servicios solicitados
- Servicios pendientes de asignación
- Servicios en proceso
- Servicios completados

### Para el Acompañante
- Total de servicios asignados
- Servicios activos
- Servicios completados
- Tasa de finalización

### Para el Sistema
- Total de NFTs creados
- Distribución por estados
- Tasa de finalización global
- Servicios activos vs completados

---

## 🎯 Tips de Optimización

1. **Batch de consultas**: Use el endpoint de estadísticas en lugar de consultas individuales
2. **Cache de estados**: Los estados solo cambian con transacciones, pueden cachearse
3. **Monitoreo de gas**: Revise los logs de transacciones para optimizar costos
4. **URIs por estado**: Configure URIs diferentes para representar visualmente cada estado

---

**Última actualización:** Enero 2025  
**Versión:** 1.0 (Refactorizada)