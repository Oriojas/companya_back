# 🧪 Suite de Pruebas para Backend NFT Servicios

Scripts de pruebas automatizadas para verificar todos los endpoints del backend FastAPI del contrato NFT de servicios de acompañamiento a adultos mayores.

## 📋 Archivos de Pruebas

### `test_backend_completo.py`
**Prueba completa de todos los endpoints** del backend en secuencia lógica.

**Características:**
- ✅ Prueba todos los 17 endpoints documentados
- ✅ Flujo completo de creación y gestión de un servicio
- ✅ Manejo de errores y validaciones
- ✅ Logging detallado en tiempo real
- ✅ Generación de reporte JSON con resultados
- ✅ Compatible con Arbitrum Sepolia

**Endpoints probados:**
1. `/health` - Health check del sistema
2. `/info/contrato` - Información del contrato
3. `/info/cuenta` - Información de la cuenta ejecutora
4. `/configuracion/uri-estado` - Configuración de URIs
5. `/servicios/crear` - Creación de nuevo servicio
6. `/servicios/{tokenId}/estado` - Consulta de estado
7. `/servicios/{tokenId}/uri` - Consulta de URI
8. `/servicios/{tokenId}/asignar-acompanante` - Asignación de acompañante
9. `/servicios/{tokenId}/acompanante` - Consulta de acompañante
10. `/servicios/{tokenId}/cambiar-estado` - Cambio de estado progresivo
11. `/servicios/{tokenId}/calificacion` - Consulta de calificación
12. `/servicios/{tokenId}/marcar-pagado` - Marcar como pagado
13. `/servicios/{tokenId}/evidencia` - Consulta de evidencia
14. `/servicios/usuario/{address}` - Servicios por usuario
15. `/logs/transacciones` - Logs de transacciones
16. `/logs/estadisticas` - Estadísticas de logs

## 🚀 Ejecución de Pruebas

### Prerrequisitos
1. **Backend ejecutándose** en `http://localhost:8000`
2. **Variables de entorno** configuradas correctamente en `.env`
3. **Wallet con ETH suficiente** para gas fees en Arbitrum Sepolia
4. **Python 3.8+** con dependencias instaladas

### Instalación de Dependencias
```bash
cd backend
pip install -r requirements.txt
```

### Ejecutar Pruebas Completas
```bash
cd tests
python test_backend_completo.py
```

### Configuración Personalizada
Puedes modificar las variables en `test_backend_completo.py`:
```python
BASE_URL = "http://localhost:8000"  # URL del backend
TEST_DESTINATARIO = "0x..."         # Dirección del destinatario
TEST_ACOMPANANTE = "0x..."          # Dirección del acompañante
```

## 📊 Resultados Esperados

### Flujo de Servicio Completo
1. **CREADO** (estado 1) → Servicio creado exitosamente
2. **ENCONTRADO** (estado 2) → Acompañante asignado
3. **TERMINADO** (estado 3) → Servicio completado
4. **CALIFICADO** (estado 4) → Calificación aplicada (1-5)
5. **PAGADO** (estado 5) → NFT de evidencia creado automáticamente

### Salida de Ejemplo
```
🚀 INICIANDO PRUEBAS COMPLETAS DEL BACKEND NFT SERVICIOS
============================================================
2024-01-15 10:30:45 - ✅ PASÓ: Health Check
2024-01-15 10:30:45 - ✅ PASÓ: Información del Contrato
2024-01-15 10:30:45 - ✅ PASÓ: Información de Cuenta
...
📊 RESUMEN DE PRUEBAS
============================================================
Total de pruebas: 17
Pruebas exitosas: 17
Pruebas fallidas: 0
Tasa de éxito: 100.0%

📁 Resultados guardados en: test_results_20240115_103045.json
```

## 📁 Archivos Generados

### `test_results_YYYYMMDD_HHMMSS.json`
Archivo JSON con resultados detallados de todas las pruebas:
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "base_url": "http://localhost:8000",
  "test_destinatario": "0x...",
  "test_acompanante": "0x...",
  "created_token_id": 5,
  "evidence_token_id": 6,
  "results": [
    {
      "timestamp": "2024-01-15 10:30:45",
      "test": "Health Check",
      "success": true,
      "details": {...}
    }
  ]
}
```

## 🔧 Troubleshooting

### Errores Comunes

**"No se puede conectar al backend"**
- Verifica que el backend esté ejecutándose: `python main.py`
- Confirma que esté en el puerto 8000

**"Insufficient balance for gas"**
- El wallet necesita ETH en Arbitrum Sepolia
- Obtener ETH de testnet: https://faucet.quicknode.com/arbitrum/sepolia

**"Invalid address format"**
- Verifica que las direcciones en el script tengan formato válido (0x...)

**Transacciones fallidas**
- Revisa los logs del backend para detalles específicos
- Verifica que el contrato esté desplegado y verificado

### Verificación Manual
Si alguna prueba falla, puedes verificar manualmente:
```bash
# Health check
curl http://localhost:8000/health

# Información del contrato
curl http://localhost:8000/info/contrato

# Logs de transacciones
curl http://localhost:8000/logs/transacciones?limit=5
```

## 📝 Notas Importantes

- ⚠️ **Cada prueba ejecuta transacciones reales** que gastan gas
- ⚠️ **Se requiere ETH suficiente** para completar todas las pruebas
- ✅ **Las pruebas son idempotentes** - pueden ejecutarse múltiples veces
- 📊 **Se genera un nuevo servicio** en cada ejecución para evitar conflictos
- 🔄 **Los token IDs son secuenciales** - incrementan con cada ejecución
- ⏱️ **Tiempo estimado**: 2-5 minutos para completar todas las pruebas

## 🎯 Uso en CI/CD

Para integración continua, puedes usar:
```bash
# Ejecutar y verificar código de salida
python test_backend_completo.py
if [ $? -eq 0 ]; then
    echo "✅ Todas las pruebas pasaron"
else
    echo "❌ Algunas pruebas fallaron"
    exit 1
fi
```

## 📞 Soporte

Para problemas o preguntas:
1. Revisa los logs del backend en `server.log`
2. Consulta `BACKEND_README.md` para documentación completa
3. Verifica las transacciones en Arbiscan usando los hashes generados

---

**Versión:** 1.0.0 | **Última actualización:** Enero 2024 | **Compatibilidad:** Backend v2.0.0+