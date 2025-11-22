# 🛠️ Filecoin Cloud Troubleshooting Guide

Guía rápida para solucionar problemas comunes con Filecoin Cloud en la aplicación IPFS Storage.

## 🚨 Problema: "Failed to authenticate with Filecoin Cloud"

### ✅ Soluciones Paso a Paso

#### 1. **Verificar Variables de Entorno**

```bash
# Revisar archivo .env
cat .env | grep FILECOIN
```

**Debe contener:**
```bash
FILECOIN_PRIVATE_KEY=tu_private_key_SIN_0x
FILECOIN_RPC_URL=https://filecoin-calibration.chainup.net/rpc/v1
```

**❌ Errores Comunes:**
- Private key con prefijo `0x` (debe removerse)
- Private key incompleto o inválido
- Espacios o caracteres extra en las variables

#### 2. **Verificar Node.js**

```bash
# Verificar versión (debe ser 18+)
node --version

# Si no está instalado o es versión antigua:
# Instalar desde https://nodejs.org/
```

#### 3. **Configurar Bridge Service**

```bash
# Ir a directorio bridge
cd bridge

# Instalar dependencias
npm install

# Verificar instalación
ls node_modules/@filoz/synapse-sdk
```

#### 4. **Iniciar Bridge Service**

```bash
# Desde directorio bridge
npm start

# Debe mostrar:
# ✅ Synapse SDK initialized successfully
# 🚀 Filecoin Bridge Service running on port 3001
```

#### 5. **Obtener Tokens de Prueba**

```bash
# Visitar faucets para obtener tokens:
# https://faucet.calibration.fildev.network/
```

**Necesitas:**
- **tFIL** para gas fees
- **USDFC** para storage payments

## 🔧 Diagnóstico Automático

```bash
# Ejecutar diagnóstico completo
python troubleshoot_filecoin.py
```

## 🚀 Setup Completo desde Cero

### Paso 1: Configurar .env

```bash
# Copiar template
cp .env.example .env

# Editar con tus credenciales
nano .env
```

Agregar:
```bash
STORAGE_PROVIDER=filecoin
FILECOIN_PRIVATE_KEY=tu_private_key_sin_0x
FILECOIN_RPC_URL=https://filecoin-calibration.chainup.net/rpc/v1
```

### Paso 2: Configurar Bridge

```bash
# Configurar bridge automáticamente
cd bridge
./setup.sh
```

### Paso 3: Obtener Tokens

1. Ve a: https://faucet.calibration.fildev.network/
2. Conecta tu wallet o pega tu dirección
3. Solicita **tFIL** y **USDFC**
4. Espera confirmación (puede tomar minutos)

### Paso 4: Setup Automático

```bash
# Volver a directorio principal
cd ..

# Ejecutar configuración completa
python setup_filecoin.py
```

### Paso 5: Probar Conexión

```bash
# Probar ambos proveedores
python test_providers.py
```

## ❌ Errores Específicos y Soluciones

### Error: "Bridge service not responding"

```bash
# Verificar si el puerto está ocupado
lsof -i :3001

# Matar proceso si es necesario
kill -9 $(lsof -t -i:3001)

# Reiniciar bridge
cd bridge && npm start
```

### Error: "Network error during upload"

```bash
# 1. Verificar conexión internet
ping google.com

# 2. Probar RPC directamente
curl -X POST https://filecoin-calibration.chainup.net/rpc/v1 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"Filecoin.Version","params":[],"id":1}'
```

### Error: "Insufficient balance"

```bash
# Verificar balance
python -c "
import requests
r = requests.get('http://localhost:3001/balance')
print(r.json())
"

# Si balance es bajo:
# 1. Obtener más tokens del faucet
# 2. Esperar confirmación en blockchain
```

### Error: "File is empty (0 bytes)"

- Verificar que el archivo tiene contenido
- Filecoin requiere mínimo 127 bytes por archivo
- El sistema automáticamente hace padding si es necesario

### Error: "Failed to initialize Synapse SDK"

```bash
# 1. Verificar private key
echo $FILECOIN_PRIVATE_KEY | wc -c  # Debe ser 65 (64 + newline)

# 2. Verificar permisos wallet
# 3. Probar con otra private key si es necesario
```

## 🔍 Comandos de Diagnóstico

### Verificar Estado General

```bash
# Estado del bridge
curl http://localhost:3001/health

# Balance de wallet
curl http://localhost:3001/balance

# Info de storage
curl http://localhost:3001/info
```

### Logs del Bridge Service

```bash
# Ver logs en tiempo real (si usas npm start)
cd bridge
npm start

# O revisar logs del proceso
ps aux | grep "node server.js"
```

### Test de Upload Mínimo

```bash
# Test rápido de upload
python -c "
import sys
sys.path.append('modules')
from filecoin_client import FilecoinCloudClient

client = FilecoinCloudClient()
print('Connection:', client.test_authentication())

# Test upload pequeño
test_data = b'Hello Filecoin!' + b'x' * 120  # 127+ bytes
cid = client.upload_file(test_data, 'test.txt')
print('Upload CID:', cid)
"
```

## 📞 Ayuda Adicional

### Recursos Útiles

- **Filecoin Docs**: https://docs.filecoin.io
- **Synapse SDK**: https://docs.filecoin.cloud
- **Calibration Faucet**: https://faucet.calibration.fildev.network/
- **Explorer**: https://calibration.filscan.io/

### Logs Importantes

```bash
# Ver logs de la aplicación Streamlit
# (los errores aparecen en la terminal donde ejecutas streamlit)

# Ver logs del bridge service
cd bridge && npm start

# Ver archivos de log
ls uploads/logs/
```

### Información de Contacto

Si los problemas persisten después de seguir esta guía:

1. Ejecuta `python troubleshoot_filecoin.py` y guarda el output
2. Verifica que tienes tokens suficientes en el faucet
3. Revisa que no hay firewalls bloqueando puerto 3001
4. Consulta la documentación oficial de Filecoin

## 🎯 Checklist Rápido

- [ ] ✅ Node.js 18+ instalado
- [ ] ✅ Variables .env configuradas correctamente  
- [ ] ✅ Bridge dependencies instaladas (`cd bridge && npm install`)
- [ ] ✅ Bridge service corriendo (`npm start`)
- [ ] ✅ Tokens tFIL y USDFC obtenidos del faucet
- [ ] ✅ Bridge responde a health check (`curl localhost:3001/health`)
- [ ] ✅ Autenticación exitosa
- [ ] ✅ Balance suficiente para operaciones

Si todos los checkmarks están completados, Filecoin Cloud debería funcionar correctamente en tu aplicación Streamlit.