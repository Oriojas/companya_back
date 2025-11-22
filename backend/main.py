import json
import os

from dotenv import load_dotenv
from eth_account import Account
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transaction_logger import log_transaction
from web3 import Web3

load_dotenv()

app = FastAPI(
    title="NFT Servicios API - Refactorizado",
    description="API simplificada para gestionar NFTs de servicios de acompañamiento (3 estados)",
    version="2.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL", "https://sepolia-rollup.arbitrum.io/rpc")
CHAIN_ID = int(os.getenv("CHAIN_ID", "421614"))

# Cargar dirección del contrato desde despliegue
deployment_file = os.path.join(
    os.path.dirname(__file__), "..", "deployments", "latest-deployment.json"
)
with open(deployment_file, "r") as f:
    deployment_info = json.load(f)
    CONTRACT_ADDRESS = deployment_info["contractAddress"]

# Inicializar Web3
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Validar conexión
if not web3.is_connected():
    raise ConnectionError("No se pudo conectar a la red Arbitrum")
else:
    print(f"🌐 Conectado a Arbitrum Sepolia - Block: {web3.eth.block_number}")

# Cargar ABI desde artifacts de Hardhat
try:
    artifact_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "artifacts",
        "contracts",
        "ColeccionServiciosNFT.sol",
        "ColeccionServiciosNFT.json",
    )
    with open(artifact_path, "r") as f:
        artifact = json.load(f)
        CONTRACT_ABI = artifact["abi"]
except FileNotFoundError:
    raise FileNotFoundError(
        f"No se encontró el ABI del contrato en {artifact_path}. "
        "Asegúrate de ejecutar 'npm run compile' en la carpeta raíz del proyecto."
    )

# Inicializar contrato
contract = web3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=CONTRACT_ABI
)

# Obtener cuenta desde clave privada
if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY no configurada en .env")

account = web3.eth.account.from_key(PRIVATE_KEY)
ACCOUNT_ADDRESS = account.address
print(f"👤 Cuenta configurada: {ACCOUNT_ADDRESS}")
print(f"📄 Contrato configurado: {CONTRACT_ADDRESS}")


# ==================== MODELOS SIMPLIFICADOS ====================
class CrearServicioRequest(BaseModel):
    destinatario: str


class CambiarEstadoRequest(BaseModel):
    nuevoEstado: int


class ConfigurarURIRequest(BaseModel):
    estado: int
    nuevaURI: str


class AsignarAcompananteRequest(BaseModel):
    acompanante: str


# ==================== FUNCIONES AUXILIARES ====================
def build_and_send_transaction(function_call):
    """Construye y envía una transacción"""
    try:
        print(f"🔧 Estimando gas para transacción...")
        nonce = web3.eth.get_transaction_count(ACCOUNT_ADDRESS)
        print(f"📝 Nonce obtenido: {nonce}")

        gas_estimate = function_call.estimate_gas({"from": ACCOUNT_ADDRESS})
        print(f"⛽ Gas estimado: {gas_estimate}")

        gas_price = web3.eth.gas_price
        print(f"💰 Gas price: {gas_price}")

        tx_dict = function_call.build_transaction(
            {
                "nonce": nonce,
                "gas": int(gas_estimate * 1.2),
                "gasPrice": gas_price,
                "from": ACCOUNT_ADDRESS,
                "chainId": CHAIN_ID,
            }
        )
        print(f"📄 Transacción construida: {tx_dict}")

        signed_tx = web3.eth.account.sign_transaction(tx_dict, PRIVATE_KEY)
        print(f"✍️ Transacción firmada")

        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"📤 Transacción enviada: {tx_hash.hex()}")

        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Recibo obtenido: {receipt}")

        tx_result = {
            "transactionHash": tx_hash.hex(),
            "blockNumber": receipt["blockNumber"],
            "gasUsed": receipt["gasUsed"],
            "status": receipt["status"],
        }

        return tx_result
    except Exception as e:
        print(f"❌ Error en build_and_send_transaction: {str(e)}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        raise HTTPException(status_code=400, detail=f"Error en transacción: {str(e)}")


# ==================== ENDPOINTS - GESTIÓN DE SERVICIOS ====================
@app.post("/servicios/crear")
async def crear_servicio(request: CrearServicioRequest):
    """
    Crear Servicio NFT - Estado: CREADO (1)

    Crea un nuevo NFT de servicio para la dirección especificada.
    Estado inicial: CREADO (1)

    - **Gasta gas** - Transacción en blockchain
    - **Retorna**: tokenId, destinatario, estado, información de transacción
    """
    try:
        print(f"🎯 Iniciando creación de servicio para: {request.destinatario}")
        destinatario = Web3.to_checksum_address(request.destinatario)
        print(f"✅ Dirección validada: {destinatario}")

        function = contract.functions.crearServicio(destinatario)
        print(f"📋 Función del contrato preparada")

        tx_result = build_and_send_transaction(function)
        print(f"✅ Transacción completada: {tx_result}")

        # Obtener tokenId del evento
        receipt = web3.eth.get_transaction_receipt(tx_result["transactionHash"])
        logs = contract.events.ServicioCreado().process_receipt(receipt)
        print(f"📊 Logs del evento: {logs}")

        token_id = logs[0]["args"]["tokenId"] if logs else None
        print(f"🎫 Token ID obtenido: {token_id}")

        # Registrar transacción en el log
        log_transaction(
            tx_hash=tx_result["transactionHash"],
            function_name="crearServicio",
            parameters={"destinatario": destinatario},
            result={"tokenId": token_id, "estado": 1, **tx_result},
            status="success" if tx_result["status"] == 1 else "failed",
        )

        return {
            "success": True,
            "tokenId": token_id,
            "destinatario": destinatario,
            "estado": 1,
            "estadoNombre": "CREADO",
            "transaction": tx_result,
        }
    except Exception as e:
        print(f"❌ Error en crear_servicio: {str(e)}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        raise HTTPException(
            status_code=400, detail=f"Error al crear servicio: {str(e)}"
        )


@app.post("/servicios/{tokenId}/asignar-acompanante")
async def asignar_acompanante(tokenId: int, request: AsignarAcompananteRequest):
    """
    Asignar Acompañante y Transferir NFT

    - Asigna acompañante al servicio
    - Cambia automáticamente a estado ENCONTRADO
    - TRANSFIERE el NFT al acompañante

    - **Gasta gas** - Transacción en blockchain
    - **Retorna**: tokenId, acompañante, estado, información de transacción
    """
    try:
        print(f"🎯 Asignando acompañante {request.acompanante} al token {tokenId}")
        acompanante = Web3.to_checksum_address(request.acompanante)
        print(f"✅ Dirección validada: {acompanante}")

        function = contract.functions.asignarAcompanante(tokenId, acompanante)
        tx_result = build_and_send_transaction(function)

        # Obtener eventos
        receipt = web3.eth.get_transaction_receipt(tx_result["transactionHash"])
        estado_logs = contract.events.EstadoCambiado().process_receipt(receipt)
        acompanante_logs = contract.events.AcompananteAsignado().process_receipt(
            receipt
        )

        # Registrar transacción en el log
        log_transaction(
            tx_hash=tx_result["transactionHash"],
            function_name="asignarAcompanante",
            parameters={"tokenId": tokenId, "acompanante": acompanante},
            result={"tokenId": tokenId, "nuevoEstado": 2, **tx_result},
            status="success" if tx_result["status"] == 1 else "failed",
        )

        return {
            "success": True,
            "tokenId": tokenId,
            "acompanante": acompanante,
            "nuevoEstado": 2,
            "estadoNombre": "ENCONTRADO",
            "nftTransferido": True,
            "transaction": tx_result,
        }
    except Exception as e:
        print(f"❌ Error en asignar_acompanante: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/servicios/{tokenId}/cambiar-estado")
async def cambiar_estado_servicio(tokenId: int, request: CambiarEstadoRequest):
    """
    Cambiar Estado del Servicio (Simplificado)

    Estados válidos:
    - 1 = CREADO (inicial)
    - 2 = ENCONTRADO (con acompañante)
    - 3 = FINALIZADO (servicio completado)

    - **Gasta gas** - Transacción en blockchain
    - **Retorna**: estado anterior, nuevo estado, información de transacción
    """
    try:
        if request.nuevoEstado not in [1, 2, 3]:
            raise ValueError("Estado debe ser 1, 2 o 3")

        print(f"🎯 Cambiando estado del token {tokenId} a {request.nuevoEstado}")

        function = contract.functions.cambiarEstadoServicio(
            tokenId, request.nuevoEstado
        )
        tx_result = build_and_send_transaction(function)

        # Obtener eventos
        receipt = web3.eth.get_transaction_receipt(tx_result["transactionHash"])
        logs = contract.events.EstadoCambiado().process_receipt(receipt)

        estado_anterior = logs[0]["args"]["estadoAnterior"] if logs else None

        estados_map = {1: "CREADO", 2: "ENCONTRADO", 3: "FINALIZADO"}

        # Registrar transacción en el log
        log_transaction(
            tx_hash=tx_result["transactionHash"],
            function_name="cambiarEstadoServicio",
            parameters={
                "tokenId": tokenId,
                "nuevoEstado": request.nuevoEstado,
            },
            result={
                "estadoAnterior": estado_anterior,
                "nuevoEstado": request.nuevoEstado,
                **tx_result,
            },
            status="success" if tx_result["status"] == 1 else "failed",
        )

        return {
            "success": True,
            "tokenId": tokenId,
            "estadoAnterior": estado_anterior,
            "estadoAnteriorNombre": estados_map.get(estado_anterior, "DESCONOCIDO"),
            "nuevoEstado": request.nuevoEstado,
            "nuevoEstadoNombre": estados_map.get(request.nuevoEstado, "DESCONOCIDO"),
            "transaction": tx_result,
        }
    except Exception as e:
        print(f"❌ Error en cambiar_estado_servicio: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/servicios/{tokenId}/finalizar")
async def finalizar_servicio(tokenId: int):
    """
    Finalizar Servicio (Atajo)

    Cambia directamente el estado a FINALIZADO (3).
    Solo funciona si está en estado ENCONTRADO (2).

    - **Gasta gas** - Transacción en blockchain
    """
    try:
        print(f"🎯 Finalizando servicio {tokenId}")

        function = contract.functions.finalizarServicio(tokenId)
        tx_result = build_and_send_transaction(function)

        # Registrar transacción
        log_transaction(
            tx_hash=tx_result["transactionHash"],
            function_name="finalizarServicio",
            parameters={"tokenId": tokenId},
            result={"tokenId": tokenId, "nuevoEstado": 3, **tx_result},
            status="success" if tx_result["status"] == 1 else "failed",
        )

        return {
            "success": True,
            "tokenId": tokenId,
            "nuevoEstado": 3,
            "estadoNombre": "FINALIZADO",
            "transaction": tx_result,
        }
    except Exception as e:
        print(f"❌ Error en finalizar_servicio: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== ENDPOINTS - CONSULTAS ====================
@app.get("/servicios/{tokenId}/estado")
async def obtener_estado_servicio(tokenId: int):
    """
    Obtener Estado del Servicio

    Consulta el estado actual de un servicio NFT.

    - **Sin gas** - Solo lectura
    - **Retorna**: estado numérico (1-3) y nombre del estado
    """
    try:
        estado = contract.functions.obtenerEstadoServicio(tokenId).call()
        estados_map = {
            1: "CREADO",
            2: "ENCONTRADO",
            3: "FINALIZADO",
        }
        return {
            "tokenId": tokenId,
            "estado": estado,
            "estadoNombre": estados_map.get(estado, "DESCONOCIDO"),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/servicios/{tokenId}/acompanante")
async def obtener_acompanante(tokenId: int):
    """
    Obtener Acompañante Asignado

    - **Sin gas** - Solo lectura
    - **Retorna**: dirección del acompañante asignado
    """
    try:
        acompanante = contract.functions.obtenerAcompanante(tokenId).call()
        return {
            "tokenId": tokenId,
            "acompanante": acompanante
            if acompanante != "0x0000000000000000000000000000000000000000"
            else None,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/servicios/{tokenId}/uri")
async def obtener_uri_servicio(tokenId: int):
    """
    Obtener URI del Servicio

    - **Sin gas** - Solo lectura
    - **URI dinámica**: Cambia según el estado del servicio
    """
    try:
        uri = contract.functions.obtenerURIServicio(tokenId).call()
        return {"tokenId": tokenId, "uri": uri}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/servicios/{tokenId}/info")
async def obtener_info_completa(tokenId: int):
    """
    Obtener Información Completa del Servicio

    - **Sin gas** - Solo lectura
    - **Retorna**: propietario, estado, acompañante, URI
    """
    try:
        info = contract.functions.obtenerInfoCompleta(tokenId).call()
        propietario, estado, acompanante, uri = info

        estados_map = {1: "CREADO", 2: "ENCONTRADO", 3: "FINALIZADO"}

        return {
            "tokenId": tokenId,
            "propietario": propietario,
            "estado": estado,
            "estadoNombre": estados_map.get(estado, "DESCONOCIDO"),
            "acompanante": acompanante
            if acompanante != "0x0000000000000000000000000000000000000000"
            else None,
            "uri": uri,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== ENDPOINTS - ESTADÍSTICAS (NUEVOS) ====================
@app.get("/estadisticas/{wallet}")
async def obtener_estadisticas_wallet(wallet: str):
    """
    Obtener Estadísticas Completas de una Wallet

    Retorna:
    - Todos los NFTs que posee
    - Estados de cada servicio
    - Resumen estadístico
    - Historial de servicios

    - **Sin gas** - Solo lectura
    """
    try:
        wallet_address = Web3.to_checksum_address(wallet)
        print(f"🔍 Consultando estadísticas para wallet: {wallet_address}")

        # Obtener datos del contrato
        result = contract.functions.obtenerServiciosConEstados(wallet_address).call()
        tokenIds, estados, acompanantes = result

        # Obtener estadísticas agregadas
        stats = contract.functions.obtenerEstadisticasWallet(wallet_address).call()
        total, creados, encontrados, finalizados = stats

        # Construir respuesta detallada
        servicios = []
        estados_map = {1: "CREADO", 2: "ENCONTRADO", 3: "FINALIZADO"}

        for i in range(len(tokenIds)):
            if tokenIds[i] >= 0:  # Incluir todos los tokens válidos
                estado_nombre = estados_map.get(estados[i], "DESCONOCIDO")
                acompanante_clean = (
                    acompanantes[i]
                    if acompanantes[i] != "0x0000000000000000000000000000000000000000"
                    else None
                )

                servicios.append(
                    {
                        "tokenId": int(tokenIds[i]),
                        "estado": int(estados[i]),
                        "estadoNombre": estado_nombre,
                        "acompanante": acompanante_clean,
                    }
                )

        return {
            "wallet": wallet_address,
            "estadisticas": {
                "totalServicios": int(total),
                "serviciosCreados": int(creados),
                "serviciosEncontrados": int(encontrados),
                "serviciosFinalizados": int(finalizados),
                "porcentajeCompletado": round(
                    (finalizados / total * 100) if total > 0 else 0, 2
                ),
            },
            "servicios": servicios,
            "resumen": {
                "serviciosActivos": int(creados + encontrados),
                "serviciosCompletados": int(finalizados),
                "tieneServiciosEnProceso": (creados + encontrados) > 0,
            },
        }
    except Exception as e:
        print(f"❌ Error en obtener_estadisticas_wallet: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/estadisticas/general/resumen")
async def obtener_resumen_general():
    """
    Obtener Resumen General del Sistema

    Estadísticas globales del contrato

    - **Sin gas** - Solo lectura
    """
    try:
        print("🔍 Generando resumen general del sistema")
        proximo_token = contract.functions.obtenerProximoTokenId().call()

        # Contar estados
        conteo_estados = {1: 0, 2: 0, 3: 0}
        for token_id in range(proximo_token):
            try:
                estado = contract.functions.obtenerEstadoServicio(token_id).call()
                if estado in conteo_estados:
                    conteo_estados[estado] += 1
            except:
                continue

        total_servicios = sum(conteo_estados.values())

        return {
            "totalNFTsCreados": proximo_token,
            "totalServiciosActivos": total_servicios,
            "estadisticasPorEstado": {
                "creados": conteo_estados[1],
                "encontrados": conteo_estados[2],
                "finalizados": conteo_estados[3],
            },
            "metricas": {
                "tasaFinalizacion": round(
                    (conteo_estados[3] / total_servicios * 100)
                    if total_servicios > 0
                    else 0,
                    2,
                ),
                "tasaAsignacion": round(
                    ((conteo_estados[2] + conteo_estados[3]) / total_servicios * 100)
                    if total_servicios > 0
                    else 0,
                    2,
                ),
                "serviciosEnProceso": conteo_estados[1] + conteo_estados[2],
            },
        }
    except Exception as e:
        print(f"❌ Error en obtener_resumen_general: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/servicios/usuario/{usuarioAddress}")
async def obtener_servicios_usuario(usuarioAddress: str):
    """
    Listar Servicios por Usuario (Compatible)

    - **Sin gas** - Solo lectura
    - **Retorna**: lista de tokenIds que posee el usuario
    """
    try:
        # Redirigir a la nueva función de estadísticas
        stats = await obtener_estadisticas_wallet(usuarioAddress)

        servicios = [servicio["tokenId"] for servicio in stats["servicios"]]

        return {
            "usuario": usuarioAddress,
            "cantidad": len(servicios),
            "servicios": servicios,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al obtener servicios: {str(e)}"
        )


# ==================== ENDPOINTS - CONFIGURACIÓN ====================
@app.post("/configuracion/uri-estado")
async def configurar_uri_estado(request: ConfigurarURIRequest):
    """
    Configurar URI por Estado

    Estados válidos: 1=CREADO, 2=ENCONTRADO, 3=FINALIZADO

    - **Gasta gas** - Transacción en blockchain
    """
    try:
        if request.estado not in [1, 2, 3]:
            raise ValueError("Estado debe ser 1, 2 o 3")

        print(f"🎯 Configurando URI para estado {request.estado}: {request.nuevaURI}")

        function = contract.functions.configurarURIEstado(
            request.estado, request.nuevaURI
        )
        tx_result = build_and_send_transaction(function)

        # Registrar transacción en el log
        log_transaction(
            tx_hash=tx_result["transactionHash"],
            function_name="configurarURIEstado",
            parameters={"estado": request.estado, "nuevaURI": request.nuevaURI},
            result={"estado": request.estado, **tx_result},
            status="success" if tx_result["status"] == 1 else "failed",
        )

        estados_map = {1: "CREADO", 2: "ENCONTRADO", 3: "FINALIZADO"}

        return {
            "success": True,
            "estado": request.estado,
            "estadoNombre": estados_map.get(request.estado),
            "uri": request.nuevaURI,
            "transaction": tx_result,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== ENDPOINTS - INFORMACIÓN DEL SISTEMA ====================
@app.get("/info/contrato")
async def obtener_info_contrato():
    """
    Información del Contrato

    - **Sin gas** - Solo lectura
    """
    try:
        nombre = contract.functions.name().call()
        simbolo = contract.functions.symbol().call()
        proximo_token_id = contract.functions.obtenerProximoTokenId().call()

        return {
            "contractAddress": CONTRACT_ADDRESS,
            "nombre": nombre,
            "simbolo": simbolo,
            "proximoTokenId": proximo_token_id,
            "chainId": CHAIN_ID,
            "rpcUrl": RPC_URL,
            "version": "2.0.0 - Refactorizado",
            "estados": {"1": "CREADO", "2": "ENCONTRADO", "3": "FINALIZADO"},
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/info/cuenta")
async def obtener_info_cuenta():
    """
    Información de Cuenta Ejecutora

    - **Sin gas** - Solo lectura
    """
    try:
        balance = web3.eth.get_balance(ACCOUNT_ADDRESS)
        balance_eth = web3.from_wei(balance, "ether")

        return {
            "address": ACCOUNT_ADDRESS,
            "balanceWei": balance,
            "balanceETH": float(balance_eth),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Health Check del Sistema

    - **Sin gas** - Solo lectura
    """
    try:
        is_connected = web3.is_connected()
        block_number = web3.eth.block_number if is_connected else None

        return {
            "status": "healthy" if is_connected else "disconnected",
            "connected": is_connected,
            "blockNumber": block_number,
            "chainId": CHAIN_ID,
            "version": "2.0.0 - Refactorizado",
            "features": {
                "estadosSimplificados": True,
                "transferenciaAutomatica": True,
                "estadisticasAvanzadas": True,
                "calificacionesEliminadas": True,
            },
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ==================== ENDPOINTS DE LOGS ====================
@app.get("/logs/transacciones")
async def obtener_logs_transacciones(limit: int = 50):
    """
    Historial de Transacciones

    - **Sin gas** - Solo lectura
    """
    try:
        from transaction_logger import get_transaction_history

        transactions = get_transaction_history(limit)
        return {"total": len(transactions), "transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo logs: {str(e)}")


@app.get("/logs/estadisticas")
async def obtener_estadisticas_logs():
    """
    Estadísticas de Logs

    - **Sin gas** - Solo lectura
    """
    try:
        from transaction_logger import get_statistics

        stats = get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}"
        )


@app.get("/logs/transaccion/{tx_hash}")
async def obtener_transaccion_por_hash(tx_hash: str):
    """
    Buscar Transacción por Hash

    - **Sin gas** - Solo lectura
    """
    try:
        from transaction_logger import get_transaction_by_hash

        transaction = get_transaction_by_hash(tx_hash)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error buscando transacción: {str(e)}"
        )


# ==================== ENDPOINTS DE MIGRACIÓN/COMPATIBILIDAD ====================
@app.get("/info/cambios")
async def obtener_info_cambios():
    """
    Información de Cambios en la Refactorización

    Documenta los cambios entre la versión 1.0 y 2.0
    """
    return {
        "version": "2.0.0",
        "fechaRefactor": "2025-01",
        "cambiosPrincipales": {
            "estadosEliminados": ["CALIFICADO", "PAGADO"],
            "estadosActuales": ["CREADO", "ENCONTRADO", "FINALIZADO"],
            "nuevasFuncionalidades": [
                "Transferencia automática de NFT",
                "Estadísticas avanzadas por wallet",
                "Resumen general del sistema",
            ],
            "funcionesEliminadas": [
                "obtenerCalificacionServicio",
                "obtenerEvidenciaServicio",
                "marcarComoPagado",
            ],
            "endpointsNuevos": [
                "GET /estadisticas/{wallet}",
                "GET /estadisticas/general/resumen",
                "POST /servicios/{id}/finalizar",
                "GET /servicios/{id}/info",
                "GET /info/cambios",
            ],
        },
        "breaking_changes": {
            "eliminados": [
                "POST /servicios/{id}/marcar-pagado",
                "GET /servicios/{id}/calificacion",
                "GET /servicios/{id}/evidencia",
            ],
            "modificados": [
                "POST /servicios/{id}/cambiar-estado (sin parámetro calificacion)",
                "POST /servicios/{id}/asignar-acompanante (ahora transfiere NFT)",
            ],
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
