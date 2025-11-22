# Colección NFT para Servicios de Acompañamiento a Adultos Mayores

## Descripción
Contrato NFT ERC-721 que representa servicios de acompañamiento para adultos mayores. Cada NFT es un servicio individual con estados dinámicos y sistema de calificación.

**🚀 Framework: Hardhat**
**🌐 Red: Arbitrum Sepolia**

Este contrato es un MVP para una hackathon que permite crear, gestionar y calificar servicios de acompañamiento a través de NFTs con estados dinámicos.

## ✅ Estado Actual

**Contrato Desplegado Exitosamente**
- **Dirección**: `0x7644e99486CDb68aaA86F6756DfD4c08577B4fB0`
- **Red**: Arbitrum Sepolia (Chain ID: 421614)
- **Hash de Transacción**: `0xa9c60c4cfb2703db88e3061f65ee518cc482072353913ef9a3b6579fcad072d7`
- **Bloque**: 217648856
- **Verificado**: ✅ Código disponible en Arbiscan

**Ver en Arbiscan**: https://sepolia.arbiscan.io/address/0x7644e99486CDb68aaA86F6756DfD4c08577B4fB0

## Estados del Servicio
- **1 = CREADO**: Servicio registrado pero no iniciado
- **2 = ENCONTRADO**: Profesional asignado al servicio  
- **3 = TERMINADO**: Servicio completado
- **4 = CALIFICADO**: Servicio evaluado con calificación 1-5
- **5 = PAGADO**: Servicio pagado (crea automáticamente un NFT de evidencia para el acompañante)

## 🔄 Flujo de Estados del Servicio NFT

```mermaid
flowchart TD
    A[Inicio] --> B[POST /servicios/crear]
    B --> C[Estado: CREADO<br/>NFT creado para destinatario]
    
    C --> D[POST /servicios/{id}/asignar-acompanante]
    D --> E[Estado: ENCONTRADO<br/>Acompañante asignado]
    
    E --> F[POST /servicios/{id}/cambiar-estado]
    F --> G[Estado: TERMINADO<br/>Servicio completado]
    
    G --> H[POST /servicios/{id}/cambiar-estado]
    H --> I[Estado: CALIFICADO<br/>Calificación 1-5 aplicada]
    
    I --> J[POST /servicios/{id}/marcar-pagado]
    J --> K[Estado: PAGADO<br/>NFT de evidencia creado]
    
    K --> L[Fin del Flujo]
    
    %% Consultas disponibles en cualquier estado
    C -.-> M[GET /servicios/{id}/estado]
    E -.-> M
    G -.-> M
    I -.-> M
    K -.-> M
    
    M --> N[GET /servicios/{id}/calificacion]
    M --> O[GET /servicios/{id}/acompanante]
    M --> P[GET /servicios/{id}/evidencia]
    M --> Q[GET /servicios/{id}/uri]
    
    %% Configuración de metadatos
    R[POST /configuracion/uri-estado] -.-> S[URIs configuradas<br/>para cada estado]
    S -.-> C
    S -.-> E
    S -.-> G
    S -.-> I
    S -.-> K
    
    style A fill:#e1f5fe
    style L fill:#f3e5f5
    style B fill:#c8e6c9
    style D fill:#c8e6c9
    style F fill:#c8e6c9
    style H fill:#c8e6c9
    style J fill:#c8e6c9
    style R fill:#fff3e0
    style M fill:#fce4ec
    style N fill:#fce4ec
    style O fill:#fce4ec
    style P fill:#fce4ec
    style Q fill:#fce4ec
```

### 📋 Explicación del Flujo

**Endpoints de Cambio de Estado (POST - Gastan Gas):**
- 🟢 **Verde**: Transiciones principales entre estados
- Cada cambio de estado es una transacción en blockchain

**Endpoints de Consulta (GET - Sin Gas):**
- 🟣 **Rosa**: Consultas disponibles en cualquier estado
- Solo lectura, no modifican el estado

**Configuración (POST - Gastan Gas):**
- 🟠 **Naranja**: Configuración de metadatos por estado
- Define las URIs que cambian según el estado del servicio

### 🎯 Progresión de Estados
1. **CREADO** → **ENCONTRADO** → **TERMINADO** → **CALIFICADO** → **PAGADO**
2. Cada estado requiere el anterior para avanzar
3. El estado **PAGADO** crea automáticamente un NFT de evidencia
4. Las consultas están disponibles en cualquier momento

## Características Principales
- ✅ Sistema de estados progresivos para servicios
- ✅ Calificación numérica 1-5 en estado CALIFICADO
- ✅ Creación automática de NFT de evidencia al pagar
- ✅ URIs dinámicas que cambian según el estado
- ✅ Compatible con Arbitrum Sepolia
- ✅ Desplegado y verificado con Hardhat
- ✅ Scripts simplificados para despliegue y verificación
- ✅ Backend FastAPI integrado y probado
- ✅ Sistema de logs automatizado

## Funciones Principales

### Creación de Servicios
```solidity
function crearServicio(address destinatario) public returns (uint256)
```
Crea un nuevo NFT de servicio para la dirección especificada.

### Gestión de Estados
```solidity
function cambiarEstadoServicio(uint256 tokenId, uint8 nuevoEstado, uint8 calificacion) public
```
Cambia el estado de un servicio. La calificación (1-5) solo se usa en estado CALIFICADO.

```solidity
function marcarComoPagado(uint256 tokenId) public
```
Marca un servicio como pagado (solo si está calificado).

### Asignación de Acompañante
```solidity
function asignarAcompanante(uint256 tokenId, address acompanante) public
```
Asigna un acompañante a un servicio específico.

### Configuración de Metadatos
```solidity
function configurarURIEstado(uint8 estado, string memory nuevaURI) public
```
Configura la URI de metadatos para cada estado del servicio.

### Consultas
```solidity
function obtenerEstadoServicio(uint256 tokenId) public view returns (uint8)
function obtenerCalificacionServicio(uint256 tokenId) public view returns (uint8)
function obtenerAcompanante(uint256 tokenId) public view returns (address)
function obtenerEvidenciaServicio(uint256 tokenId) public view returns (uint256)
```

## 🛠️ Instalación y Uso

### Requisitos
- Node.js >= 16.0.0
- npm >= 8.0.0

### Instalación Rápida
```bash
npm install
cp .env.example .env
# Editar .env con tus credenciales
npm run compile
npm run deploy
```

Para detalles completos, consulta **QUICK_START.md**

### Backend Python (Separado)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python check_config.py
python main.py
```

## 🔧 Scripts Disponibles

| Comando | Descripción |
|---------|-------------|
| `npm run compile` | Compila el contrato |
| `npm run deploy` | **Despliegue en Arbitrum Sepolia** |
| `npm run verify` | **Verificación en Arbiscan** |

## 📡 Endpoints del Backend

### 🔄 Cambio de Estados (POST - Gastan Gas)
| Endpoint | Estado Resultante | Descripción |
|----------|------------------|-------------|
| `POST /servicios/crear` | **CREADO** (1) | Crea nuevo NFT de servicio |
| `POST /servicios/{id}/asignar-acompanante` | **ENCONTRADO** (2) | Asigna acompañante al servicio |
| `POST /servicios/{id}/cambiar-estado` | **TERMINADO** (3) | Marca servicio como completado |
| `POST /servicios/{id}/cambiar-estado` | **CALIFICADO** (4) | Evalúa servicio (calificación 1-5) |
| `POST /servicios/{id}/marcar-pagado` | **PAGADO** (5) | Marca como pagado (crea NFT evidencia) |

### 🔍 Consultas (GET - Sin Gas)
| Endpoint | Descripción |
|----------|-------------|
| `GET /servicios/{id}/estado` | Estado actual del servicio |
| `GET /servicios/{id}/calificacion` | Calificación del servicio |
| `GET /servicios/{id}/acompanante` | Acompañante asignado |
| `GET /servicios/{id}/evidencia` | NFT de evidencia generado |
| `GET /servicios/{id}/uri` | URI de metadatos actual |
| `GET /servicios/usuario/{address}` | Todos los servicios de un usuario |

### ⚙️ Configuración (POST - Gastan Gas)
| Endpoint | Descripción |
|----------|-------------|
| `POST /configuracion/uri-estado` | Configura URI para cada estado (1-5) |

### ℹ️ Información del Sistema (GET - Sin Gas)
| Endpoint | Descripción |
|----------|-------------|
| `GET /health` | Estado de salud del sistema |
| `GET /info/contrato` | Información del contrato |
| `GET /info/cuenta` | Información de la cuenta ejecutora |
| `GET /logs/transacciones` | Historial de transacciones |
| `GET /logs/estadisticas` | Estadísticas de uso |

## 📁 Estructura del Proyecto

```
companya_back/
├── contracts/
│   └── ColeccionServiciosNFT.sol          # Contrato principal
├── scripts/
│   ├── deploy.js                          # **Script de despliegue**
│   └── verify.js                          # **Script de verificación**
├── deployments/                           # Información de despliegues (generado)
├── backend/                              # API FastAPI completa
│   ├── main.py                          # Servidor principal
│   ├── transaction_logger.py            # Sistema de logs
│   ├── check_config.py                  # Verificador de configuración
│   └── tests/                           # Suite de pruebas
├── artifacts/                           # ABI y bytecode (generado)
├── hardhat.config.js                     # Configuración de Hardhat
├── package.json                          # Dependencias
├── .env.example                          # Template de variables
├── .gitignore                            # Archivos a ignorar
├── README.md                             # Este archivo
└── QUICK_START.md                        # Guía rápida
```

## 🚀 Scripts Principales

### Despliegue
```bash
npm run deploy
```

**Funcionalidades:**
- ✅ Verificación de configuración y balance
- ✅ Compilación automática del contrato
- ✅ Despliegue seguro en Arbitrum Sepolia
- ✅ Gestión de archivos de despliegue
- ✅ Generación de enlaces útiles

### Verificación
```bash
npm run verify
```

**Funcionalidades:**
- ✅ Verificación automática en Arbiscan
- ✅ Uso de API key para verificación
- ✅ Manejo de errores y casos ya verificados
- ✅ Enlaces para verificación manual

### Flujo de Trabajo Recomendado
1. **Compilar**: `npm run compile`
2. **Desplegar**: `npm run deploy`
3. **Verificar**: `npm run verify`

## 🔐 Configuración

### Contrato (npm)
Copia y configura `.env`:
```env
# Network Configuration
ARBITRUM_SEPOLIA_RPC_URL=https://sepolia-rollup.arbitrum.io/rpc

# Private Key (SIN el prefijo 0x)
PRIVATE_KEY=tu_clave_privada_sin_0x

# Verification API Keys (opcional)
ARBISCAN_API_KEY=tu_arbiscan_api_key_here
```

### Backend (Python)
Copia `backend/.env.example` a `backend/.env`:
```env
# Network Configuration
RPC_URL=https://sepolia-rollup.arbitrum.io/rpc

# Private Key (REQUIRED - without 0x prefix)
PRIVATE_KEY=tu_clave_privada_sin_0x

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## 🎯 Ejemplo de Uso con curl

### Flujo Completo de un Servicio:
```bash
# 1. Crear servicio (Estado: CREADO)
curl -X POST "http://localhost:8000/servicios/crear" \
  -H "Content-Type: application/json" \
  -d '{"destinatario": "0x..."}'

# 2. Asignar acompañante (Estado: ENCONTRADO)
curl -X POST "http://localhost:8000/servicios/1/asignar-acompanante" \
  -H "Content-Type: application/json" \
  -d '{"acompanante": "0x..."}'

# 3. Cambiar a TERMINADO
curl -X POST "http://localhost:8000/servicios/1/cambiar-estado" \
  -H "Content-Type: application/json" \
  -d '{"nuevoEstado": 3, "calificacion": 0}'

# 4. Cambiar a CALIFICADO con calificación 5
curl -X POST "http://localhost:8000/servicios/1/cambiar-estado" \
  -H "Content-Type: application/json" \
  -d '{"nuevoEstado": 4, "calificacion": 5}'

# 5. Marcar como PAGADO (crea NFT evidencia)
curl -X POST "http://localhost:8000/servicios/1/marcar-pagado"

# 6. Consultar estado final
curl "http://localhost:8000/servicios/1/estado"

# 7. Verificar NFT de evidencia
curl "http://localhost:8000/servicios/1/evidencia"
```

## 📖 Documentación

- **QUICK_START.md** - Guía rápida para desplegar en 5 minutos
- **backend/BACKEND_README.md** - Documentación completa del backend
- **plan_trabajo_nft.md** - Plan técnico y arquitectura del sistema

## 🔐 Seguridad

- **NUNCA** hagas commit del archivo `.env`
- **NUNCA** compartas tu `PRIVATE_KEY`
- Usa wallets separadas para testnet y mainnet
- Verifica todas las transacciones en Arbiscan antes de producción

## 🌐 Enlaces Útiles

- **Arbiscan Sepolia**: https://sepolia.arbiscan.io/
- **Faucet ETH**: https://faucet.quicknode.com/arbitrum/sepolia
- **OpenSea Testnet**: https://testnets.opensea.io/
- **Hardhat Docs**: https://hardhat.org/
- **Solidity Docs**: https://docs.soliditylang.org/

## 📝 Próximos Pasos

1. ✅ Desplegar contrato en Arbitrum Sepolia
2. ✅ Verificar contrato en Arbiscan
3. ✅ Configurar y probar backend FastAPI
4. ✅ Ejecutar suite completa de pruebas
5. ⭕ Integrar con frontend
6. ⭕ Preparar para producción

## 📞 Soporte

Para problemas o preguntas:
1. Consulta **QUICK_START.md** para guía rápida
2. Revisa **plan_trabajo_nft.md** para detalles técnicos
3. Verifica los logs de error
4. Consulta la documentación de Hardhat

---

**Fecha de Despliegue**: 2025
**Estado**: ✅ COMPLETADO Y FUNCIONAL
**Red**: Arbitrum Sepolia Testnet
**Framework**: Hardhat