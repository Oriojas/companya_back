# NFT IPFS Metadata Uploader

Una aplicación web construida con Streamlit para subir imágenes a IPFS y generar metadata compatible con OpenSea para NFTs.

## 🎯 Características

- **Upload de imágenes**: Sube imágenes directamente a IPFS usando Pinata
- **Generación de metadata**: Crea metadata JSON compatible con estándares de OpenSea
- **Interfaz amigable**: Aplicación web intuitiva con Streamlit
- **Atributos personalizados**: Formulario específico para atributos de NFT
- **Historial de uploads**: Mantiene registro de todas las subidas
- **URIs IPFS**: Genera URIs finales para usar en smart contracts

## 📁 Estructura del Proyecto

```
IPFS_storage/
├── modules/
│   ├── __init__.py
│   ├── pinata_client.py      # Cliente para API de Pinata
│   └── metadata_builder.py   # Generador de metadata OpenSea
├── uploads/
│   ├── temp_images/          # Imágenes temporales
│   └── metadata_history/     # Historial y JSONs generados
├── app.py                    # Aplicación Streamlit principal
├── requirements.txt          # Dependencias Python
├── .env                      # Variables de entorno (no incluido)
├── .env.example             # Template de configuración
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

Copia el archivo `.env.example` a `.env` y configura tus credenciales de Pinata:

```bash
cp .env.example .env
```

Edita el archivo `.env`:

```bash
PINATA_API_KEY=tu_api_key_aqui
PINATA_SECRET_API_KEY=tu_secret_api_key_aqui
```

### 5. Obtener credenciales de Pinata

1. Ve a [Pinata Cloud](https://app.pinata.cloud)
2. Crea una cuenta gratuita (1GB gratis)
3. Navega a **Developers > API Keys**
4. Crea un nuevo API key con permisos de:
   - `pinFileToIPFS`
   - `pinJSONToIPFS`
   - `pinList`
   - `userPinnedDataTotal`
5. Copia el API Key y Secret API Key al archivo `.env`

## 🖥️ Uso

### Ejecutar la aplicación

```bash
# Asegúrate de que el entorno virtual esté activado
source venv/bin/activate

# Ejecutar la aplicación
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

### Flujo de trabajo

1. **Subir imagen**: Arrastra o selecciona una imagen (PNG, JPG, GIF, SVG, WEBP)
2. **Completar metadata**: Llena el formulario con:
   - **Name**: Nombre del NFT
   - **Description**: Descripción detallada
   - **Actividad**: Tipo de actividad
   - **Usuario**: Usuario asociado
   - **Acompañante**: Compañero o equipo
   - **Tiempo**: Valor numérico de tiempo
3. **Upload a IPFS**: Haz clic en "🚀 Upload to IPFS"
4. **Obtener URIs**: Copia la URI final para usar en tu smart contract

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

### Validaciones
- Formato de archivos soportados
- Tamaño máximo (100MB para Pinata)
- Campos requeridos
- Estructura de metadata

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

## 📈 Límites y Consideraciones

### Pinata (Plan Gratuito)
- **Almacenamiento**: 1GB
- **Ancho de banda**: 1GB/mes
- **Archivos**: Sin límite en cantidad
- **Tamaño máximo por archivo**: 100MB

### Recomendaciones
- Optimiza imágenes antes de subir
- Usa formatos eficientes (WebP, PNG optimizado)
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

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para detalles.

## 📞 Soporte

Para reportar bugs o solicitar features:

1. Abre un issue en GitHub
2. Proporciona pasos para reproducir el problema
3. Incluye logs de error si es posible

---

**¡Feliz creación de NFTs! 🎨✨**