// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

/**
 * @title ColeccionServiciosNFT
 * @dev Contrato NFT simplificado para servicios de acompañamiento a adultos mayores
 * @notice Version refactorizada para hackathon con 3 estados simplificados
 */
contract ColeccionServiciosNFT is ERC721URIStorage {
    // ============================================
    // CONSTANTES Y VARIABLES DE ESTADO
    // ============================================

    // Estados simplificados: 1=CREADO, 2=ENCONTRADO, 3=FINALIZADO
    uint8 public constant ESTADO_CREADO = 1;
    uint8 public constant ESTADO_ENCONTRADO = 2;
    uint8 public constant ESTADO_FINALIZADO = 3;

    // Mappings principales
    mapping(uint256 => uint8) public estadosServicios;
    mapping(uint256 => address) public acompanantesServicios;
    mapping(uint8 => string) public URIsPorEstado;

    // Contador de tokens
    uint256 private _nextTokenId;

    // ============================================
    // EVENTOS
    // ============================================

    event ServicioCreado(uint256 indexed tokenId, address indexed destinatario);

    event EstadoCambiado(
        uint256 indexed tokenId,
        uint8 estadoAnterior,
        uint8 nuevoEstado
    );

    event AcompananteAsignado(
        uint256 indexed tokenId,
        address indexed acompanante
    );

    event URIEstadoConfigurada(uint8 estado, string nuevaURI);

    // ============================================
    // CONSTRUCTOR
    // ============================================

    constructor() ERC721("ColeccionServiciosNFT", "CSNFT") {}

    // ============================================
    // FUNCIONES PRINCIPALES
    // ============================================

    /**
     * @dev Crea un nuevo servicio NFT en estado CREADO
     * @param destinatario Dirección que recibirá el NFT inicialmente
     * @return tokenId ID del nuevo NFT creado
     */
    function crearServicio(address destinatario) public returns (uint256) {
        require(destinatario != address(0), "Destinatario invalido");

        uint256 tokenId = _nextTokenId++;
        _safeMint(destinatario, tokenId);

        // Inicializar en estado CREADO
        estadosServicios[tokenId] = ESTADO_CREADO;
        acompanantesServicios[tokenId] = address(0);

        // Establecer URI para estado CREADO si existe
        if (bytes(URIsPorEstado[ESTADO_CREADO]).length > 0) {
            _setTokenURI(tokenId, URIsPorEstado[ESTADO_CREADO]);
        }

        emit ServicioCreado(tokenId, destinatario);
        return tokenId;
    }

    /**
     * @dev Asigna un acompañante y transfiere automáticamente el NFT
     * @param tokenId ID del servicio
     * @param acompanante Dirección del acompañante que recibirá el NFT
     */
    function asignarAcompanante(uint256 tokenId, address acompanante) public {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        require(acompanante != address(0), "Acompanante no valido");
        require(
            estadosServicios[tokenId] == ESTADO_CREADO,
            "Servicio debe estar en CREADO"
        );

        // Asignar acompañante
        acompanantesServicios[tokenId] = acompanante;

        // Cambiar automáticamente a estado ENCONTRADO
        uint8 estadoAnterior = estadosServicios[tokenId];
        estadosServicios[tokenId] = ESTADO_ENCONTRADO;

        // TRANSFERIR NFT al acompañante
        address propietarioActual = ownerOf(tokenId);
        _transfer(propietarioActual, acompanante, tokenId);

        // Actualizar URI para estado ENCONTRADO
        if (bytes(URIsPorEstado[ESTADO_ENCONTRADO]).length > 0) {
            _setTokenURI(tokenId, URIsPorEstado[ESTADO_ENCONTRADO]);
        }

        emit EstadoCambiado(tokenId, estadoAnterior, ESTADO_ENCONTRADO);
        emit AcompananteAsignado(tokenId, acompanante);
    }

    /**
     * @dev Cambia el estado de un servicio (simplificado)
     * @param tokenId ID del servicio
     * @param nuevoEstado Nuevo estado (1, 2 o 3)
     */
    function cambiarEstadoServicio(uint256 tokenId, uint8 nuevoEstado) public {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        require(
            nuevoEstado >= ESTADO_CREADO && nuevoEstado <= ESTADO_FINALIZADO,
            "Estado invalido"
        );

        uint8 estadoAnterior = estadosServicios[tokenId];

        // Validar transiciones permitidas
        if (nuevoEstado == ESTADO_ENCONTRADO) {
            require(
                estadoAnterior == ESTADO_CREADO,
                "Servicio debe estar en CREADO"
            );
            require(
                acompanantesServicios[tokenId] != address(0),
                "Acompanante no asignado"
            );
        } else if (nuevoEstado == ESTADO_FINALIZADO) {
            require(
                estadoAnterior == ESTADO_ENCONTRADO,
                "Servicio debe estar en ENCONTRADO"
            );
        }

        // Actualizar estado
        estadosServicios[tokenId] = nuevoEstado;

        // Actualizar URI según el nuevo estado
        if (bytes(URIsPorEstado[nuevoEstado]).length > 0) {
            _setTokenURI(tokenId, URIsPorEstado[nuevoEstado]);
        }

        emit EstadoCambiado(tokenId, estadoAnterior, nuevoEstado);
    }

    /**
     * @dev Finaliza un servicio (atajo para cambiar a estado FINALIZADO)
     * @param tokenId ID del servicio a finalizar
     */
    function finalizarServicio(uint256 tokenId) public {
        cambiarEstadoServicio(tokenId, ESTADO_FINALIZADO);
    }

    // ============================================
    // FUNCIONES DE CONFIGURACIÓN
    // ============================================

    /**
     * @dev Configura la URI para un estado específico
     * @param estado Estado (1, 2 o 3)
     * @param nuevaURI Nueva URI para el estado
     */
    function configurarURIEstado(uint8 estado, string memory nuevaURI) public {
        require(
            estado >= ESTADO_CREADO && estado <= ESTADO_FINALIZADO,
            "Estado invalido"
        );
        URIsPorEstado[estado] = nuevaURI;
        emit URIEstadoConfigurada(estado, nuevaURI);
    }

    // ============================================
    // FUNCIONES DE CONSULTA
    // ============================================

    /**
     * @dev Obtiene el estado actual de un servicio
     * @param tokenId ID del servicio
     * @return Estado actual (1, 2 o 3)
     */
    function obtenerEstadoServicio(
        uint256 tokenId
    ) public view returns (uint8) {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        return estadosServicios[tokenId];
    }

    /**
     * @dev Obtiene el acompañante asignado a un servicio
     * @param tokenId ID del servicio
     * @return Dirección del acompañante
     */
    function obtenerAcompanante(uint256 tokenId) public view returns (address) {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        return acompanantesServicios[tokenId];
    }

    /**
     * @dev Obtiene la URI actual de un servicio
     * @param tokenId ID del servicio
     * @return URI del servicio
     */
    function obtenerURIServicio(
        uint256 tokenId
    ) public view returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        return tokenURI(tokenId);
    }

    // ============================================
    // FUNCIONES DE ESTADÍSTICAS
    // ============================================

    /**
     * @dev Obtiene todos los servicios de una wallet con sus estados
     * @param wallet Dirección a consultar
     * @return tokenIds Array de IDs de tokens
     * @return estados Array de estados correspondientes
     * @return acompanantes Array de acompañantes asignados
     */
    function obtenerServiciosConEstados(
        address wallet
    )
        public
        view
        returns (
            uint256[] memory tokenIds,
            uint8[] memory estados,
            address[] memory acompanantes
        )
    {
        uint256 balance = balanceOf(wallet);
        tokenIds = new uint256[](balance);
        estados = new uint8[](balance);
        acompanantes = new address[](balance);

        uint256 index = 0;
        for (uint256 i = 0; i < _nextTokenId && index < balance; i++) {
            if (_ownerOf(i) == wallet) {
                tokenIds[index] = i;
                estados[index] = estadosServicios[i];
                acompanantes[index] = acompanantesServicios[i];
                index++;
            }
        }

        return (tokenIds, estados, acompanantes);
    }

    /**
     * @dev Obtiene estadísticas agregadas de una wallet
     * @param wallet Dirección a consultar
     * @return totalServicios Total de servicios NFTs
     * @return serviciosCreados Cantidad en estado CREADO
     * @return serviciosEncontrados Cantidad en estado ENCONTRADO
     * @return serviciosFinalizados Cantidad en estado FINALIZADO
     */
    function obtenerEstadisticasWallet(
        address wallet
    )
        public
        view
        returns (
            uint256 totalServicios,
            uint256 serviciosCreados,
            uint256 serviciosEncontrados,
            uint256 serviciosFinalizados
        )
    {
        totalServicios = balanceOf(wallet);

        for (uint256 i = 0; i < _nextTokenId; i++) {
            if (_ownerOf(i) == wallet) {
                uint8 estado = estadosServicios[i];
                if (estado == ESTADO_CREADO) {
                    serviciosCreados++;
                } else if (estado == ESTADO_ENCONTRADO) {
                    serviciosEncontrados++;
                } else if (estado == ESTADO_FINALIZADO) {
                    serviciosFinalizados++;
                }
            }
        }

        return (
            totalServicios,
            serviciosCreados,
            serviciosEncontrados,
            serviciosFinalizados
        );
    }

    /**
     * @dev Verifica si una wallet tiene servicios activos (no finalizados)
     * @param wallet Dirección a consultar
     * @return true si tiene servicios activos
     */
    function tieneServiciosActivos(address wallet) public view returns (bool) {
        for (uint256 i = 0; i < _nextTokenId; i++) {
            if (
                _ownerOf(i) == wallet &&
                estadosServicios[i] != ESTADO_FINALIZADO
            ) {
                return true;
            }
        }
        return false;
    }

    // ============================================
    // FUNCIONES AUXILIARES
    // ============================================

    /**
     * @dev Obtiene el próximo ID de token que será asignado
     * @return Próximo token ID
     */
    function obtenerProximoTokenId() public view returns (uint256) {
        return _nextTokenId;
    }

    /**
     * @dev Obtiene información completa de un servicio
     * @param tokenId ID del servicio
     * @return propietario Dueño actual del NFT
     * @return estado Estado actual
     * @return acompanante Acompañante asignado
     * @return uri URI de metadatos
     */
    function obtenerInfoCompleta(
        uint256 tokenId
    )
        public
        view
        returns (
            address propietario,
            uint8 estado,
            address acompanante,
            string memory uri
        )
    {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");

        propietario = ownerOf(tokenId);
        estado = estadosServicios[tokenId];
        acompanante = acompanantesServicios[tokenId];
        uri = tokenURI(tokenId);

        return (propietario, estado, acompanante, uri);
    }

    // ============================================
    // OVERRIDES NECESARIOS
    // ============================================

    /**
     * @dev Override de tokenURI para compatibilidad
     */
    function tokenURI(
        uint256 tokenId
    ) public view override returns (string memory) {
        return super.tokenURI(tokenId);
    }

    /**
     * @dev Override de supportsInterface para compatibilidad
     */
    function supportsInterface(
        bytes4 interfaceId
    ) public view override returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
