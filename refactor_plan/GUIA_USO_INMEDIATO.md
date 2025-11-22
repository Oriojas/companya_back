# 🚀 Guía de Uso Inmediato - Sistema NFT Refactorizado
## Para Hackathon - Versión Simplificada

---

## 📋 Información del Sistema

### ✅ Estado Actual
- **Contrato Desplegado**: `0x4b4E49792eBc60156A65EB7b028be1F8553D6f98`
- **Red**: Arbitrum Sepolia
- **Estados**: 3 simplificados (CREADO, ENCONTRADO, FINALIZADO)
- **Versión**: 2.0.0 - Refactorizado

### 🎯 Cambio Principal
**El NFT se transfiere automáticamente al acompañante cuando se le asigna el servicio**

---

## ⚡ Inicio Rápido (5 minutos)

### 1. Verificar Backend
```bash
cd backend
python3 check_config.py
# Debe mostrar: "Configuration check passed!"
```

### 2. Iniciar Backend
```bash
cd backend
python3 main.py
# Debe mostrar: "Uvicorn running on http://0.0.0.0:8000"
```

### 3. Probar Health Check
```bash
curl http://localhost:8000/health
# Respuesta esperada: {"status": "healthy", "version": "2.0.0 - Refactorizado"}
```

---

## 🔄 Flujo Completo Simplificado

### Paso 1: Crear Servicio
```bash
curl -X POST "http://localhost:8000/servicios/crear" \
  -H "Content-Type: application/json" \
  -d '{"destinatario": "0xa92d504731aA3E99DF20ffd200ED03F9a55a6219"}'
```

**Resultado**: NFT creado en estado CREADO, propiedad del cliente

### Paso 2: Asignar Acompañante (¡NFT se transfiere automáticamente!)
```bash
curl -X POST "http://localhost:8000/servicios/1/asignar-acompanante" \
  -H "Content-Type: application/json" \
  -d '{"acompanante": "0x742D35cc6634c0532925A3B8d4b6a5f6c6d5b7C8"}'
```

**Resultado**: Estado cambia a ENCONTRADO + NFT transferido al acompañante

### Paso 3: Finalizar Servicio
```bash
curl -X POST "http://localhost:8000/servicios/1/finalizar"
```

**Resultado**: Estado cambia a FINALIZADO, servicio completo

---

## 📊 Nuevas Funcionalidades

### Ver Estadísticas de una Wallet
```bash
curl "http://localhost:8000/estadisticas/0x742D35cc6634c0532925A3B8d4b6a5f6c6d5b7C8"
```

**Muestra**:
- Total de servicios NFT que posee
- Estados de cada servicio
- Porcentaje de completado
- Servicios activos vs finalizados

### Resumen General del Sistema
```bash
curl "http://localhost:8000/estadisticas/general/resumen"
```

**Muestra**:
- Total de NFTs creados
- Distribución por estados
- Métricas del sistema

---

## 🎯 Ejemplos para Demo

### Demo Completa (Cliente + Acompañante)
```python
import requests

BASE_URL = "http://localhost:8000"
cliente = "0xa92d504731aA3E99DF20ffd200ED03F9a55a6219"
acompanante = "0x742D35cc6634c0532925A3B8d4b6a5f6c6d5b7C8"

# 1. Cliente solicita servicio
response = requests.post(f"{BASE_URL}/servicios/crear", 
                        json={"destinatario": cliente})
token_id = response.json()["tokenId"]
print(f"✅ Servicio creado: Token {token_id}")

# 2. Sistema asigna acompañante (NFT se transfiere)
response = requests.post(f"{BASE_URL}/servicios/{token_id}/asignar-acompanante",
                        json={"acompanante": acompanante})
print(f"✅ NFT transferido al acompañante")

# 3. Servicio se completa
response = requests.post(f"{BASE_URL}/servicios/{token_id}/finalizar")
print(f"✅ Servicio finalizado")

# 4. Ver estadísticas del acompañante
response = requests.get(f"{BASE_URL}/estadisticas/{acompanante}")
stats = response.json()
print(f"📊 Acompañante tiene {stats['estadisticas']['totalServicios']} servicios")
```

### Demo de Dashboard Administrativo
```bash
# Resumen del sistema
curl "http://localhost:8000/estadisticas/general/resumen" | jq .

# Ver todos los logs de transacciones
curl "http://localhost:8000/logs/transacciones?limit=10" | jq .

# Estado de salud del sistema
curl "http://localhost:8000/health" | jq .
```

---

## 🔧 Endpoints Principales

### Gestión Básica
- `POST /servicios/crear` - Crear servicio
- `POST /servicios/{id}/asignar-acompanante` - Asignar + transferir NFT
- `POST /servicios/{id}/finalizar` - Finalizar servicio

### Consultas
- `GET /servicios/{id}/estado` - Ver estado actual
- `GET /servicios/{id}/info` - Info completa del servicio

### Estadísticas (Nuevas)
- `GET /estadisticas/{wallet}` - Estadísticas por wallet
- `GET /estadisticas/general/resumen` - Resumen global

### Sistema
- `GET /health` - Estado del sistema
- `GET /info/contrato` - Info del contrato
- `GET /info/cambios` - Qué cambió en la refactorización

---

## ⚠️ Cambios Importantes

### ❌ Ya NO Existe
- Calificaciones (1-5)
- NFT de evidencia separado
- Estado CALIFICADO
- Estado PAGADO
- Endpoint `/marcar-pagado`
- Endpoint `/calificacion`
- Endpoint `/evidencia`

### ✅ Nuevo Comportamiento
- **NFT se transfiere automáticamente** al asignar acompañante
- Solo 3 estados: CREADO (1) → ENCONTRADO (2) → FINALIZADO (3)
- Estadísticas completas en una sola consulta
- Flujo más directo y rápido

---

## 🚨 Para la Hackathon

### Puntos Clave para la Demo
1. **Simplicidad**: Solo 3 pasos vs 5 anteriores
2. **Transferencia automática**: El acompañante recibe el NFT inmediatamente
3. **Estadísticas ricas**: Vista completa de servicios por persona
4. **Gas optimizado**: Menos transacciones = menos costo

### Historia de Usuario
```
Como cliente:
1. Solicito un servicio → Recibo NFT
2. Sistema encuentra acompañante → Mi NFT se transfiere al acompañante
3. Servicio se completa → NFT queda como evidencia en poder del acompañante

Como acompañante:
1. Me asignan servicio → Recibo NFT automáticamente
2. Completo el servicio → NFT queda como evidencia de mi trabajo
3. Consulto mis estadísticas → Veo todos mis servicios realizados
```

---

## 🔍 Troubleshooting Rápido

### Backend no inicia
```bash
# Verificar configuración
cd backend && python3 check_config.py

# Verificar puertos
lsof -i :8000

# Logs del backend
python3 main.py 2>&1 | tee backend.log
```

### Transacciones fallan
```bash
# Verificar balance
curl "http://localhost:8000/info/cuenta" | jq .balanceETH

# Verificar conexión
curl "http://localhost:8000/health" | jq .connected
```

### NFT no se transfiere
- Verificar que el acompañante tenga dirección válida
- Usar `/servicios/{id}/info` para ver el propietario actual
- El NFT se transfiere AUTOMÁTICAMENTE al asignar acompañante

---

## 📱 URLs Útiles

### Contrato en Arbiscan
https://sepolia.arbiscan.io/address/0x4b4E49792eBc60156A65EB7b028be1F8553D6f98

### OpenSea Testnet
https://testnets.opensea.io/assets/arbitrum-sepolia/0x4b4E49792eBc60156A65EB7b028be1F8553D6f98

### Faucet para ETH de prueba
https://faucet.quicknode.com/arbitrum/sepolia

---

## 🎉 ¡Listo para la Hackathon!

El sistema está **simplificado, optimizado y listo** para desarrollo rápido:

- ✅ **Menos complejidad** = desarrollo más rápido
- ✅ **Transferencia automática** = UX mejorado
- ✅ **Estadísticas ricas** = demos más impresionantes
- ✅ **Gas optimizado** = menos costos
- ✅ **API intuitiva** = integración frontend más fácil

**¡Buen desarrollo en la hackathon! 🚀**

---

**Versión**: 2.0.0 Refactorizado  
**Fecha**: Enero 2025  
**Estado**: ✅ Listo para usar