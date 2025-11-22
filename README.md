# Colección NFT para Servicios de Acompañamiento a Adultos Mayores

## Descripción
Contrato NFT ERC-721 que representa servicios de acompañamiento para adultos mayores. Cada NFT es un servicio individual con estados dinámicos y sistema de calificación.

**🚀 Framework: Hardhat**
**🌐 Red: Arbitrum Sepolia**

Este contrato es un MVP para una hackathon que permite crear, gestionar y calificar servicios de acompañamiento a través de NFTs con estados dinámicos.

## ✅ Estado Actual

**Contrato Desplegado Exitosamente**
- **Dirección**: `0xFF2E077849546cCB392f9e38B716A40fDC451798`
- **Red**: Arbitrum Sepolia (Chain ID: 421614)
- **Hash de Transacción**: `0xde54554ac31b7e3de6b62212103aed5c1b293d6ac8335ac4917d2df01f21b161`
- **Bloque**: 217596257
- **Verificado**: ✅ Código disponible en Arbiscan

**Ver en Arbiscan**: https://sepolia.arbiscan.io/address/0xFF2E077849546cCB392f9e38B716A40fDC451798

## Estados del Servicio
- **1 = CREADO**: Servicio registrado pero no iniciado
- **2 = ENCONTRADO**: Profesional asignado al servicio  
- **3 = TERMINADO**: Servicio completado
- **4 = CALIFICADO**: Servicio evaluado con calificación 1-5
- **5 = PAGADO**: Servicio pagado (crea automáticamente un NFT de evidencia para el acompañante)

## Características Principales
- ✅ Sistema de estados progresivos para servicios
- ✅ Calificación numérica 1-5 en estado CALIFICADO
- ✅ Creación automática de NFT de evidencia al pagar
- ✅ URIs dinámicas que cambian según el estado
- ✅ Compatible con Arbitrum Sepolia
- ✅ Desplegado y verificado con Hardhat
- ✅ Scripts simplificados para despliegue y verificación

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
npm run deploy-and-verify
```

Para detalles completos, consulta **QUICK_START.md**

## 🔧 Scripts Disponibles

| Comando | Descripción |
|---------|-------------|
| `npm run compile` | Compila el contrato |
| `npm run deploy` | **Despliegue en Arbitrum Sepolia** |
| `npm run verify` | **Verificación en Arbiscan** |

## 📁 Estructura del Proyecto

```
companya_back/
├── contracts/
│   └── ColeccionServiciosNFT.sol          # Contrato principal
├── scripts/
│   ├── deploy.js                          # **Script de despliegue**
│   └── verify.js                          # **Script de verificación**
├── deployments/                           # Información de despliegues (generado)
├── abi/                                  # ABI exportado (generado)
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

## 🔐 Configuración de Variables de Entorno

Copia y configura `.env`:
```env
# Network Configuration
ARBITRUM_SEPOLIA_RPC_URL=https://sepolia-rollup.arbitrum.io/rpc

# Private Key (SIN el prefijo 0x)
PRIVATE_KEY=tu_clave_privada_sin_0x

# Verification API Keys (opcional para verificación)
ARBISCAN_API_KEY=tu_arbiscan_api_key_here
```

## 📖 Documentación

- **QUICK_START.md** - Guía rápida para desplegar en 5 minutos
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
3. ⭕ Integrar ABI en frontend/backend
4. ⭕ Realizar pruebas exhaustivas
5. ⭕ Preparar para producción

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