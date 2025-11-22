// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract ColeccionServiciosNFT is ERC721URIStorage {
    // Estados: 1=CREADO, 2=ENCONTRADO, 3=TERMINADO, 4=CALIFICADO, 5=PAGADO

    mapping(uint256 => uint8) public estadosServicios;
    mapping(uint256 => uint8) public calificacionesServicios;
    mapping(uint256 => address) public acompanantesServicios;
    mapping(uint256 => uint256) public evidenciasServicios;
    mapping(uint8 => string) public URIsPorEstado;

    uint256 private _nextTokenId;

    event ServicioCreado(uint256 indexed tokenId, address indexed destinatario);
    event EstadoCambiado(
        uint256 indexed tokenId,
        uint8 estadoAnterior,
        uint8 nuevoEstado,
        uint8 calificacion
    );
    event URIEstadoConfigurada(uint8 estado, string nuevaURI);
    event ServicioPagado(
        uint256 indexed tokenId,
        address indexed acompanante,
        uint256 indexed tokenIdEvidencia
    );

    constructor() ERC721("ColeccionServiciosNFT", "CSNFT") {}

    function crearServicio(address destinatario) public returns (uint256) {
        require(destinatario != address(0), "Destinatario invalido");

        uint256 tokenId = _nextTokenId++;
        _safeMint(destinatario, tokenId);

        estadosServicios[tokenId] = 1;
        calificacionesServicios[tokenId] = 0;
        acompanantesServicios[tokenId] = address(0);

        if (bytes(URIsPorEstado[1]).length > 0) {
            _setTokenURI(tokenId, URIsPorEstado[1]);
        }

        emit ServicioCreado(tokenId, destinatario);
        return tokenId;
    }

    function cambiarEstadoServicio(
        uint256 tokenId,
        uint8 nuevoEstado,
        uint8 calificacion
    ) public {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        require(nuevoEstado >= 1 && nuevoEstado <= 5, "Estado invalido");

        uint8 estadoAnterior = estadosServicios[tokenId];
        estadosServicios[tokenId] = nuevoEstado;

        if (nuevoEstado == 4) {
            require(
                calificacion >= 1 && calificacion <= 5,
                "Calificacion debe ser entre 1 y 5"
            );
            calificacionesServicios[tokenId] = calificacion;
        } else {
            calificacionesServicios[tokenId] = 0;
        }

        if (nuevoEstado == 5) {
            require(
                estadoAnterior == 4,
                "Servicio debe estar calificado para pagar"
            );
            address acompanante = acompanantesServicios[tokenId];
            require(acompanante != address(0), "Acompanante no asignado");

            uint256 tokenIdEvidencia = _nextTokenId++;
            _safeMint(acompanante, tokenIdEvidencia);

            estadosServicios[tokenIdEvidencia] = 5;
            calificacionesServicios[tokenIdEvidencia] = calificacionesServicios[
                tokenId
            ];
            acompanantesServicios[tokenIdEvidencia] = acompanante;

            if (bytes(URIsPorEstado[5]).length > 0) {
                _setTokenURI(tokenIdEvidencia, URIsPorEstado[5]);
            }

            evidenciasServicios[tokenId] = tokenIdEvidencia;
            emit ServicioPagado(tokenId, acompanante, tokenIdEvidencia);
        }

        if (bytes(URIsPorEstado[nuevoEstado]).length > 0) {
            _setTokenURI(tokenId, URIsPorEstado[nuevoEstado]);
        }

        emit EstadoCambiado(tokenId, estadoAnterior, nuevoEstado, calificacion);
    }

    function configurarURIEstado(uint8 estado, string memory nuevaURI) public {
        require(estado >= 1 && estado <= 5, "Estado invalido");
        URIsPorEstado[estado] = nuevaURI;
        emit URIEstadoConfigurada(estado, nuevaURI);
    }

    function obtenerEstadoServicio(
        uint256 tokenId
    ) public view returns (uint8) {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        return estadosServicios[tokenId];
    }

    function obtenerCalificacionServicio(
        uint256 tokenId
    ) public view returns (uint8) {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        return calificacionesServicios[tokenId];
    }

    function asignarAcompanante(uint256 tokenId, address acompanante) public {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        require(acompanante != address(0), "Acompanante no valido");
        acompanantesServicios[tokenId] = acompanante;
    }

    function obtenerAcompanante(uint256 tokenId) public view returns (address) {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        return acompanantesServicios[tokenId];
    }

    function obtenerEvidenciaServicio(
        uint256 tokenId
    ) public view returns (uint256) {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        return evidenciasServicios[tokenId];
    }

    function marcarComoPagado(uint256 tokenId) public {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        require(
            estadosServicios[tokenId] == 4,
            "Servicio debe estar calificado"
        );

        uint8 estadoAnterior = estadosServicios[tokenId];
        estadosServicios[tokenId] = 5;

        address acompanante = acompanantesServicios[tokenId];
        require(acompanante != address(0), "Acompanante no asignado");

        uint256 tokenIdEvidencia = _nextTokenId++;
        _safeMint(acompanante, tokenIdEvidencia);

        estadosServicios[tokenIdEvidencia] = 5;
        calificacionesServicios[tokenIdEvidencia] = calificacionesServicios[
            tokenId
        ];
        acompanantesServicios[tokenIdEvidencia] = acompanante;

        if (bytes(URIsPorEstado[5]).length > 0) {
            _setTokenURI(tokenIdEvidencia, URIsPorEstado[5]);
        }

        evidenciasServicios[tokenId] = tokenIdEvidencia;

        emit EstadoCambiado(
            tokenId,
            estadoAnterior,
            5,
            calificacionesServicios[tokenId]
        );
        emit ServicioPagado(tokenId, acompanante, tokenIdEvidencia);
    }

    function obtenerURIServicio(
        uint256 tokenId
    ) public view returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "Servicio no existe");
        return tokenURI(tokenId);
    }

    function obtenerProximoTokenId() public view returns (uint256) {
        return _nextTokenId;
    }

    function tokenURI(
        uint256 tokenId
    ) public view override returns (string memory) {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(
        bytes4 interfaceId
    ) public view override returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    // _burn function is automatically inherited from ERC721URIStorage
}
