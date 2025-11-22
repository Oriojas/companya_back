# Plan de Trabajo - Colección NFT para Servicios de Acompañamiento a Adultos Mayores

## Descripción General
Desarrollo de un contrato NFT que represente una colección completa de servicios de acompañamiento a adultos mayores. Cada NFT dentro de la colección será un servicio individual con sus propios estados independientes y URIs dinámicas que cambian según el estado del servicio.

## Arquitectura del Sistema

### Estructura de la Colección
- **Un contrato = Una colección completa**
- **Cada NFT = Un servicio individual**
- **Estados independientes por NFT**
- **URIs dinámicas por estado**

### Gestión de Estados por Servicio
Cada NFT mantiene su propio ciclo de estados:
- **creado** → Servicio registrado pero no iniciado
- **encontrado** → Profesional asignado al servicio
- **terminado** → Servicio completado
- **calificado** → Servicio evaluado y calificado
- **pagado** → Servicio pagado al acompañante

## Funcionalidades Principales

### 1. Sistema de Estados por NFT
- Estados independientes para cada token
- Transiciones controladas entre estados
- Restricciones de flujo de estados
- Consulta individual de estado por NFT

### 2. URIs Dinámicas por Estado
- URI específica para cada estado del servicio
- Metadatos que reflejan el estado actual en tiempo real
- Cambio automático de URI al cambiar estado
- Compatibilidad con estándar OpenSea

### 3. Gestión de la Colección
- Minting de nuevos servicios (NFTs)
- Control de acceso para cambios de estado
- Consulta de todos los servicios de un usuario
- Gestión de múltiples servicios simultáneos

## Estructura del Contrato NFT

### Variables de Estado
```solidity
// Estados posibles para cada servicio
enum ServiceState { CREADO, ENCONTRADO, TERMINADO, CALIFICADO }

// Mapeo de tokenId a estado actual del servicio
mapping(uint256 => ServiceState) public estadosServicios;

// Mapeo de tokenId a URI actual (cambia con el estado)
mapping(uint256 => string) public tokenURIs;

// Mapeo de tokenId a calificación (solo en estado CALIFICADO)
mapping(uint256 => uint8) public calificacionesServicios;

// Mapeo de URIs por estado (configuración global)
mapping(ServiceState => string) public URIsPorEstado;

// Contador de servicios en la colección
uint256 private _nextTokenId;
```

### Funciones Principales

#### 1. Creación de Nuevos Servicios
```solidity
function crearServicio(address destinatario) 
    public 
    onlyOwner 
    returns (uint256)
```

#### 2. Cambio de Estado Individual
```solidity
function cambiarEstadoServicio(uint256 tokenId, ServiceState nuevoEstado, uint8 calificacion) 
    public 
    onlyOwner
```

#### 3. Configuración de URIs por Estado
```solidity
function configurarURIEstado(ServiceState estado, string memory nuevaURI) 
    public 
    onlyOwner
```

#### 4. Consultas Específicas
```solidity
function obtenerEstadoServicio(uint256 tokenId) public view returns (ServiceState)
function obtenerURIServicio(uint256 tokenId) public view returns (string memory)
function obtenerCalificacionServicio(uint256 tokenId) public view returns (uint8)
function serviciosPorUsuario(address usuario) public view returns (uint256[] memory)
```

### Eventos
```solidity
event ServicioCreado(uint256 indexed tokenId, address indexed destinatario);
event EstadoCambiado(uint256 indexed tokenId, ServiceState estadoAnterior, ServiceState nuevoEstado, uint8 calificacion);
event URIEstadoConfigurada(ServiceState estado, string nuevaURI);
```

## Sistema de URIs Dinámicas

### Configuración de URIs por Estado
- **Estado CREADO**: URI para metadatos de servicio pendiente
- **Estado ENCONTRADO**: URI para metadatos de servicio en progreso
- **Estado TERMINADO**: URI para metadatos de servicio completado
- **Estado CALIFICADO**: URI para metadatos de servicio evaluado

### Comportamiento de tokenURI()
```solidity
function tokenURI(uint256 tokenId) 
    public 
    view 
    override 
    returns (string memory)
{
    // Retorna la URI actual del token basada en su estado
    return tokenURIs[tokenId];
}
```

## Estructura de Metadatos por Estado

### Ejemplo de Metadatos para Estado "CREADO"
```json
{
  "name": "Servicio de Acompañamiento #1 - Pendiente",
  "description": "Servicio de acompañamiento para adultos mayores - Estado: Pendiente de asignación",
  "image": "https://tu-plataforma.com/imagenes/estado-creado.png",
  "attributes": [
    {
      "trait_type": "Estado del Servicio",
      "value": "creado"
    },
    {
      "trait_type": "Tipo",
      "value": "Acompañamiento"
    }
  ]
}
```

### Ejemplo de Metadatos para Estado "CALIFICADO"
```json
{
  "name": "Servicio de Acompañamiento #1 - Calificado",
  "description": "Servicio de acompañamiento completado y evaluado positivamente",
  "image": "https://tu-plataforma.com/imagenes/estado-calificado.png",
  "attributes": [
    {
      "trait_type": "Estado del Servicio",
      "value": "calificado"
    },
    {
      "trait_type": "Calificación",
      "value": "Excelente"
    },
    {
      "trait_type": "Puntuación",
      "display_type": "number",
      "value": 5,
      "max_value": 5
    }
  ]
}
```

## Flujo de Trabajo del Sistema

### 1. Configuración Inicial
- Desplegar contrato de colección
- Configurar URIs para cada estado
- Establecer permisos de administración

### 2. Creación de Servicios
- Owner crea nuevo NFT para representar servicio
- Estado inicial: CREADO
- URI inicial: configurada para estado CREADO

### 3. Progresión del Servicio
- Cambio a ENCONTRADO cuando se asigna profesional
- URI cambia automáticamente a la del nuevo estado
- Continúa hasta estado CALIFICADO con calificación 1-5

### 4. Visualización en OpenSea
- Cada NFT muestra metadatos específicos de su estado actual
- Cambios de estado reflejados inmediatamente en la plataforma
- Atributos dinámicos según progreso del servicio
- Calificación numérica visible en estado CALIFICADO

## Plan de Implementación

### Fase 1: Contrato Base con Estados
1. Crear contrato `ColeccionServiciosNFT`
2. Implementar sistema de estados por NFT
3. Configurar mapeos para estados y URIs individuales

### Fase 2: Sistema de URIs Dinámicas
1. Implementar configuración de URIs por estado
2. Crear función `tokenURI()` dinámica
3. Configurar cambio automático de URI al cambiar estado

### Fase 3: Gestión de Colección
1. Funciones de consulta por usuario
2. Sistema de minting de servicios
3. Control de acceso y permisos

### Fase 4: Metadatos y Compatibilidad
1. Diseñar estructuras JSON para cada estado
2. Implementar eventos ERC-4906 para actualizaciones
3. Verificar compatibilidad con OpenSea

## Consideraciones Técnicas

### Para Múltiples NFTs
- Estados independientes por token
- URIs específicas por estado y servicio
- Escalabilidad para cientos de servicios
- Consultas eficientes por usuario
- Sistema de calificación 1-5 para evaluación cuantitativa

### Metadatos Dinámicos
- Cambios reflejados en tiempo real
- Compatibilidad con estándares OpenSea
- Flexibilidad para personalizar por estado
- Soporte para diferentes tipos de servicios
- Atributo de calificación numérica con display_type "number"

## Próximos Pasos
1. Implementar contrato con estados individuales por NFT
2. Configurar sistema de URIs dinámicas
3. Crear funciones de gestión de colección
4. Desarrollar metadatos específicos por estado
5. Realizar pruebas con múltiples servicios

Este plan permite gestionar una colección completa donde cada NFT representa un servicio independiente con su propio progreso y metadatos dinámicos que cambian según el estado actual del servicio.
