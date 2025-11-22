# NFT IPFS Metadata Uploader

Una aplicación web construida con Streamlit para subir imágenes a IPFS y generar metadata compatible con OpenSea para NFTs. **Soporta múltiples proveedores de almacenamiento descentralizado.**

## 🎯 Características

- **Múltiples proveedores**: Pinata IPFS y Filecoin Cloud
- **Upload de imágenes**: Sube imágenes directamente a IPFS
- **Generación de metadata**: Crea metadata JSON compatible con estándares de OpenSea
- **Interfaz amigable**: Aplicación web intuitiva con Streamlit
- **Atributos personalizados**: Formulario específico para atributos de NFT
- **Historial de uploads**: Mantiene registro de todas las subidas
- **Sistema de logs completo**: Registro detallado en formato JSON de todos los uploads
- **URIs IPFS**: Genera URIs finales para usar en smart contracts

## 📁 Estructura del Proyecto

```
IPFS_storage/
├── modules/
│   ├── __init__.py
│   ├── pinata_client.py      # Cliente para API de Pinata
│   ├── filecoin_client.py    # Cliente para Filecoin Cloud
│   └── metadata_builder.py   # Generador de metadata OpenSea
├── bridge/                   # Servicio Node.js para Filecoin Cloud
│   ├── server.js            # Servidor bridge con Synapse SDK
│   ├── package.json         # Dependencias Node.js
│   └── setup.sh            # Script de configuración
├── uploads/
│   ├── temp_images/          # Imágenes temporales
│   ├── metadata_history/     # Historial y JSONs generados
│   └── logs/                 # Logs de uploads en formato JSON
├── app.py                    # Aplicación Streamlit principal
├── setup_filecoin.py         # Configuración de Filecoin Cloud
├── requirements.txt          # Dependencias Python
├── .env                      # Variables de entorno (no incluido)
├── .env.example             # Template de configuración
├── view_logs.py             # Visualizador de logs independiente
└── README.md                # Esta documentación
```

## 🚀 Instalación

### 1. Clonar y navegar al proyecto

```bash
cd companya_back/IPFS_storage
```

### 2. Crear entorno virtual (requerido en Ubuntu/Debian)

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo `.env.example` a `.env`:

```bash
cp .env.example .env
```

### 5. Configurar proveedor de almacenamiento

Edita el archivo `.env` según el proveedor que prefieras:

#### **Opción A: Pinata IPFS (Tradicional)**
```bash
STORAGE_PROVIDER=pinata
PINATA_API_KEY=tu_api_key_aqui
PINATA_SECRET_API_KEY=tu_secret_api_key_aqui
```

**Obtener credenciales de Pinata:**
1. Ve a [Pinata Cloud](https://app.pinata.cloud)
2. Crea cuenta gratuita (1GB gratis)
3. Crea API key con permisos completos
4. Copia las credenciales al `.env`

#### **Opción B: Filecoin Cloud (Recomendado)**
```bash
STORAGE_PROVIDER=filecoin
FILECOIN_PRIVATE_KEY=tu_private_key_sin_0x
FILECOIN_RPC_URL=https://filecoin-calibration.chainup.net/rpc/v1
```

**Configurar Filecoin Cloud:**
1. Obtén tokens de prueba: [Faucet Calibration](https://faucet.calibration.fildev.network/)
2. Configura tu private key de wallet
3. Ejecuta: `python setup_filecoin.py`

## 🖥️ Uso

### Ejecutar la aplicación

```bash
# Asegúrate de que el entorno virtual esté activado
source venv/bin/activate

# Para Filecoin Cloud (configuración inicial)
python setup_filecoin.py

# Ejecutar la aplicación
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

### Flujo de trabajo

1. **Seleccionar proveedor**: Elige entre Pinata IPFS o Filecoin Cloud
2. **Subir imagen**: Arrastra o selecciona una imagen (PNG, JPG, GIF, SVG, WEBP)
3. **Completar metadata**: Llena el formulario con:
   - **Name**: Nombre del NFT
   - **Description**: Descripción detallada
   - **Actividad**: Tipo de actividad
   - **Usuario**: Usuario asociado
   - **Acompañante**: Compañero o equipo
   - **Tiempo**: Valor numérico de tiempo
4. **Upload a IPFS**: Haz clic en "🚀 Upload to IPFS"
5. **Obtener URIs**: Copia la URI final para usar en tu smart contract
6. **Ver logs**: Revisa el tab "📊 Upload Logs" para ver estadísticas detalladas

## 📝 Formato de Metadata

La aplicación genera metadata compatible con OpenSea:

```json
{
  "name": "Mi NFT",
  "description": "Descripción del NFT",
  "image": "ipfs://QmXxxxxxxxxxx",
  "external_url": "ipfs://QmXxxxxxxxxxx",
  "attributes": [
    {"trait_type": "Actividad", "value": "Swimming"},
    {"trait_type": "Usuario", "value": "John Doe"},
    {"trait_type": "Acompanante", "value": "Maria"},
    {"trait_type": "tiempo", "value": 5}
  ]
}
```

## 🔗 URIs Generadas

Después de cada upload exitoso obtienes:

- **Image URI**: `ipfs://QmImageCID` - URI de la imagen
- **NFT Token URI**: `ipfs://QmMetadataCID` - **URI principal para smart contracts**

### Uso en Smart Contracts

```solidity
// ERC721 Example
function tokenURI(uint256 tokenId) public view returns (string) {
    return "ipfs://QmYourMetadataCID";
}
```

## 🛠️ API de Módulos

### PinataClient

```python
from modules.pinata_client import PinataClient

client = PinataClient()

# Subir archivo
image_cid = client.upload_file(file_bytes, filename)

# Subir JSON
metadata_cid = client.upload_json(json_data, name)

# Generar URI
uri = client.get_ipfs_uri(cid)  # ipfs://cid
```

### FilecoinCloudClient

```python
from modules.filecoin_client import FilecoinCloudClient

client = FilecoinCloudClient()

# Subir archivo
image_cid = client.upload_file(file_bytes, filename)

# Subir JSON
metadata_cid = client.upload_json(json_data, name)

# Generar URI
uri = client.get_ipfs_uri(cid)  # ipfs://cid

# Funciones adicionales
balance = client.get_balance()  # Obtener balance USDFC/FIL
cost = client.estimate_cost(file_size, days)  # Estimar costo
```

### MetadataBuilder

```python
from modules.metadata_builder import build_nft_metadata

metadata = build_nft_metadata(
    name="Mi NFT",
    description="Descripción",
    image_uri="ipfs://QmXxx",
    actividad="Swimming",
    usuario="John",
    acompanante="Solo",
    tiempo=10
)
```

## 📊 Características de la Interfaz

### Sidebar
- **Configuración**: Estado de conexión a Pinata
- **Account Info**: Información de tu cuenta Pinata
- **Recent Uploads**: Últimas 5 subidas

### Tabs Principales
- **🚀 Upload NFT**: Formulario de upload principal
- **📜 History**: Historial completo de uploads
- **📊 Upload Logs**: Sistema completo de logs y estadísticas

### Validaciones
- Formato de archivos soportados
- Tamaño máximo (100MB para Pinata)
- Campos requeridos
- Estructura de metadata

## 📊 Sistema de Logs

### Logs Automáticos
Cada upload (exitoso o fallido) se registra automáticamente en `uploads/logs/upload_log.json` con:

- **Información del archivo**: Nombre, tamaño, tipo
- **Datos IPFS**: CID, URI, enlaces de gateway
- **Metadata del NFT**: Información completa del token
- **Estadísticas**: Tiempo de upload, estado, errores
- **Trazabilidad**: Relación entre imágenes y metadata

### Ver Logs en la App
```
Tab "📊 Upload Logs" en Streamlit:
- 📈 Estadísticas generales
- 📄 Lista de uploads recientes
- 🔍 Filtros por tipo y estado
- 📥 Exportar logs a JSON/CSV
- 🗑️ Limpiar logs antiguos
```

### Visualizador Independiente
```bash
# Modo interactivo
python view_logs.py

# Comandos directos
python view_logs.py stats           # Estadísticas
python view_logs.py recent 20       # Últimos 20 uploads  
python view_logs.py nfts           # Pares NFT completos
python view_logs.py failed         # Uploads fallidos
python view_logs.py export json    # Exportar logs
```

### Estructura del Log
```json
{
  "timestamp": "2024-01-01T10:00:00",
  "upload_type": "image|metadata",
  "status": "success|failed",
  "filename": "image.png",
  "file_size_bytes": 1024000,
  "cid": "QmXxxxxx",
  "ipfs_uri": "ipfs://QmXxxxxx",
  "gateway_url": "https://gateway.pinata.cloud/ipfs/QmXxxxxx",
  "nft_name": "My NFT #001",
  "error": "Error message (if failed)"
}
```

## 🔧 Solución de Problemas

### Entorno virtual no activado
```
command not found: streamlit
```
**Solución**: Activa el entorno virtual con `source venv/bin/activate`

### Error de autenticación
```
❌ Failed to authenticate with Pinata API
```
**Solución**: Verifica que tu `.env` contenga las credenciales correctas.

### Error de conexión
```
❌ Error initializing Pinata client
```
**Solución**: 
1. Verifica tu conexión a internet
2. Confirma que las API keys son válidas
3. Revisa que tienes cuota disponible en Pinata

### Archivo muy grande
```
❌ File too large. Maximum size is 100MB
```
**Solución**: Reduce el tamaño de tu imagen o usa un plan pagado de Pinata.

### Formato no soportado
```
❌ Unsupported file type
```
**Solución**: Usa PNG, JPG, GIF, SVG o WEBP.

## 🌐 Gateways IPFS

Para acceder a tu contenido via HTTP:

- **Pinata Gateway**: `https://gateway.pinata.cloud/ipfs/[CID]`
- **IPFS.io Gateway**: `https://ipfs.io/ipfs/[CID]`
- **Cloudflare Gateway**: `https://cloudflare-ipfs.com/ipfs/[CID]`

### Límites y Consideraciones

### Pinata (Plan Gratuito)
- **Almacenamiento**: 1GB
- **Ancho de banda**: 1GB/mes
- **Archivos**: Sin límite en cantidad
- **Tamaño máximo por archivo**: 100MB

### Filecoin Cloud (Plan Gratuito)
- **Almacenamiento**: Hasta 1TB gratis
- **Permanencia**: Almacenamiento permanente (no suscripción)
- **Tamaño mínimo**: 127 bytes por archivo
- **CDN**: Acceso rápido mundial incluido

### Recomendaciones
- **Filecoin Cloud**: Para proyectos grandes y almacenamiento permanente
- **Pinata**: Para prototipado rápido y proyectos pequeños
- Optimiza imágenes antes de subir
- Mantén respaldo local de CIDs importantes
- Considera el costo de gas al usar URIs en mainnet

## 🔐 Seguridad

### Variables de Entorno
- **NUNCA** hardcodees API keys en el código
- Usa `.env` para credenciales locales
- En producción, usa variables de entorno del sistema

### IPFS Público
- Todo contenido subido a IPFS es **público**
- **NO** subas información sensible sin encriptar
- Los CIDs son permanentes y difíciles de eliminar

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Haz fork del repositorio
2. Crea una rama para tu feature
3. Implementa cambios con tests
4. Envía pull request

## 🧪 Testing y Debugging

### Scripts de Diagnóstico
```bash
# Configurar Filecoin Cloud
python setup_filecoin.py

# Probar conexión a Pinata
python test_connection.py

# Test de upload completo
python test_upload.py

# Ver logs detallados
python view_logs.py

# Ejemplos de uso programático
python example_usage.py
```

### Archivos de Log
- **uploads/logs/upload_log.json**: Log principal con todos los uploads
- **uploads/metadata_history/**: JSONs individuales de cada NFT
- **uploads/logs/export_*.json**: Exportaciones de logs
- **bridge/**: Servicio Node.js para Filecoin Cloud (solo si usas Filecoin)

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para detalles.

## 📞 Soporte

Para reportar bugs o solicitar features:

1. Abre un issue en GitHub
2. Proporciona pasos para reproducir el problema
3. Incluye logs de error si es posible

---

**¡Feliz creación de NFTs! 🎨✨**