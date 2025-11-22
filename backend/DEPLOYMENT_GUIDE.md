# 🚀 Guía de Despliegue - Backend NFT Servicios

Guía completa para desplegar el backend FastAPI del contrato NFT de servicios de acompañamiento a adultos mayores.

## 📋 Prerrequisitos

### Sistema Operativo
- **Linux** (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- **macOS** 10.15+
- **Windows** 10/11 (con WSL2 recomendado)

### Software Requerido
- **Python 3.8+**
- **pip** (gestor de paquetes Python)
- **git** (control de versiones)

### Verificar Instalaciones
```bash
# Verificar Python
python3 --version

# Verificar pip
pip3 --version

# Verificar git
git --version
```

## 🛠️ Instalación Manual

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd test_nft/backend
```

### 2. Crear Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows
```

### 3. Instalar Dependencias
```bash
# Actualizar pip
pip install --upgrade pip

# Instalar setuptools primero (evita problemas con web3)
pip install setuptools wheel

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
# Copiar template
cp .env.example .env

# Editar archivo .env
nano .env
```

**Contenido de `.env`:**
```
# Configuración Backend NFT Servicios
PRIVATE_KEY=tu_clave_privada_del_wallet
RPC_URL=https://sepolia-rollup.arbitrum.io/rpc
CONTRACT_ADDRESS=0xFF2E077849546cCB392f9e38B716A40fDC451798
CHAIN_ID=421614
```

### 5. Verificar Instalación
```bash
# Ejecutar diagnóstico
python diagnostic.py

# Probar dependencias
python -c "import fastapi, web3, uvicorn; print('✅ Dependencias OK')"
```

## 🤖 Despliegue Automático

### Script Básico
```bash
chmod +x deploy.sh
./deploy.sh
```

### Script Robusto (Recomendado)
```bash
chmod +x deploy_robust.sh
./deploy_robust.sh
```

## 🚀 Ejecución del Servidor

### Desarrollo (Modo Debug)
```bash
source venv/bin/activate
python main.py
```

### Producción (Con Uvicorn)
```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Producción (En Segundo Plano)
```bash
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
tail -f server.log  # Ver logs en tiempo real
```

## 📊 Verificación del Servidor

Una vez ejecutado, verifica que esté funcionando:

### Endpoints de Verificación
```bash
# Health check
curl http://localhost:8000/health

# Información del contrato
curl http://localhost:8000/info/contrato

# Documentación interactiva (Swagger)
# Abrir en navegador: http://localhost:8000/docs
```

### Respuestas Esperadas
```json
// Health check
{
  "status": "healthy",
  "connected": true,
  "blockNumber": 217627182,
  "chainId": 421614
}

// Info contrato
{
  "contractAddress": "0xFF2E077849546cCB392f9e38B716A40fDC451798",
  "nombre": "ColeccionServiciosNFT",
  "simbolo": "CSNFT",
  "proximoTokenId": 13,
  "chainId": 421614,
  "rpcUrl": "https://sepolia-rollup.arbitrum.io/rpc"
}
```

## 🧪 Pruebas Automatizadas

### Ejecutar Suite Completa
```bash
cd tests
python3 test_backend_completo.py
```

### Pruebas Individuales
```bash
# Solo health check
curl http://localhost:8000/health

# Probar creación de servicio
curl -X POST "http://localhost:8000/servicios/crear" \
  -H "Content-Type: application/json" \
  -d '{"destinatario": "0x..."}'
```

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'pkg_resources'"
**Solución:**
```bash
# Instalar setuptools manualmente
pip install setuptools

# O reinstalar todas las dependencias
pip install --force-reinstall -r requirements.txt
```

### Error: "Connection refused" o "Cannot connect to RPC"
**Solución:**
1. Verificar RPC_URL en `.env`
2. Probar conectividad:
   ```bash
   curl -X POST $RPC_URL \
     -H "Content-Type: application/json" \
     --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
   ```
3. Usar RPC alternativo si es necesario

### Error: "Insufficient balance for gas"
**Solución:**
1. Verificar balance:
   ```bash
   curl http://localhost:8000/info/cuenta
   ```
2. Obtener ETH de testnet:
   - Faucet: https://faucet.quicknode.com/arbitrum/sepolia
   - Necesario: ~0.1 ETH para pruebas

### Error: "Invalid address format"
**Solución:**
- Verificar que las direcciones comiencen con `0x`
- Usar direcciones checksum válidas
- Ejemplo válido: `0xa92d504731aA3E99DF20ffd200ED03F9a55a6219`

### Error: "Contract not found"
**Solución:**
1. Verificar CONTRACT_ADDRESS en `.env`
2. Asegurar que el ABI esté disponible:
   ```bash
   # En la carpeta raíz del proyecto
   npm run compile
   ```
3. Verificar en Arbiscan: https://sepolia.arbiscan.io/address/0xFF2E077849546cCB392f9e38B716A40fDC451798

### El Servidor No Inicia
**Solución:**
1. Verificar puerto disponible:
   ```bash
   netstat -tulpn | grep :8000
   ```
2. Cambiar puerto si es necesario:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```
3. Verificar logs:
   ```bash
   tail -f server.log
   ```

## 🔒 Configuración de Seguridad

### Variables Sensibles
- **NUNCA** commits de `.env`
- **NUNCA** compartas `PRIVATE_KEY`
- Usa diferentes wallets para testnet/mainnet

### Firewall y Red
```bash
# Abrir puerto (ejemplo Ubuntu)
sudo ufw allow 8000/tcp

# Verificar conexiones
ss -tulpn | grep :8000
```

### Variables de Entorno en Producción
```bash
# En lugar de .env, usar variables del sistema
export PRIVATE_KEY=tu_clave
export RPC_URL=tu_rpc
export CONTRACT_ADDRESS=0x...
export CHAIN_ID=421614
```

## 📈 Monitoreo y Logs

### Ver Logs en Tiempo Real
```bash
tail -f server.log
```

### Logs de Transacciones
```bash
# Ver todas las transacciones
curl http://localhost:8000/logs/transacciones

# Ver estadísticas
curl http://localhost:8000/logs/estadisticas
```

### Métricas de Salud
```bash
# Script de monitoreo simple
while true; do
  curl -s http://localhost:8000/health | jq '.'
  sleep 30
done
```

## 🐳 Docker (Opcional)

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Construir y Ejecutar
```bash
docker build -t nft-backend .
docker run -p 8000:8000 --env-file .env nft-backend
```

## 🔄 Actualizaciones

### Actualizar Código
```bash
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
```

### Reiniciar Servicio
```bash
# Encontrar proceso
ps aux | grep uvicorn

# Detener proceso
kill <PID>

# Reiniciar
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

## 📞 Soporte

### Diagnóstico Automático
```bash
python diagnostic.py
```

### Verificar Estado del Contrato
```bash
curl http://localhost:8000/info/contrato
```

### Logs Detallados
```bash
# Ver logs de aplicación
cat server.log

# Ver logs de transacciones
python view_logs.py
```

### Recursos Útiles
- **Documentación API:** http://localhost:8000/docs
- **Arbiscan Contract:** https://sepolia.arbiscan.io/address/0xFF2E077849546cCB392f9e38B716A40fDC451798
- **Faucet ETH:** https://faucet.quicknode.com/arbitrum/sepolia

---

## ✅ Checklist de Despliegue

- [ ] Python 3.8+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`requirements.txt`)
- [ ] Archivo `.env` configurado
- [ ] ABI del contrato disponible
- [ ] Wallet con ETH suficiente
- [ ] Servidor ejecutándose en puerto 8000
- [ ] Health check respondiendo
- [ ] Pruebas automatizadas pasando
- [ ] Logs funcionando correctamente

**Estado:** 🟢 **PRODUCTION READY**  
**Última actualización:** Noviembre 2025  
**Versión Backend:** 2.0.0