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
    title="NFT Servicios API",
    description="API para gestionar NFTs de servicios de acompañamiento",
    version="1.0.0",
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


# ==================== MODELOS ====================
class CrearServicioRequest(BaseModel):
    destinatario: str


class CambiarEstadoRequest(BaseModel):
    nuevoEstado: int
    calificacion: int = 0


class ConfigurarURIRequest(BaseModel):
    estado: int
    nuevaURI: str


class AsignarAcompananteRequest(BaseModel):
    tokenId: int
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


# ==================== ENDPOINTS - 1. CREAR SERVICIO ====================
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
            "transaction": tx_result,
        }
    except Exception as e:
        print(f"❌ Error en crear_servicio: {str(e)}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        raise HTTPException(
            status_code=400, detail=f"Error al crear servicio: {str(e)}"
        )


# ==================== ENDPOINTS - 2. CAMBIAR ESTADO ====================
@app.post("/servicios/{tokenId}/cambiar-estado")
async def cambiar_estado_servicio(tokenId: int, request: CambiarEstadoRequest):
    """
    Cambiar Estado del Servicio

    Cambia el estado de un servicio NFT en el flujo progresivo.

    - **Gasta gas** - Transacción en blockchain
    - **Estados**: 1=CREADO, 2=ENCONTRADO, 3=TERMINADO, 4=CALIFICADO, 5=PAGADO
    - **Calificación**: Solo aplica en estado CALIFICADO (4), valores 1-5
    - **NFT Evidencia**: Se crea automáticamente en estado PAGADO (5)
    - **Retorna**: estado anterior, nuevo estado, información de transacción
    """
    try:
        if request.nuevoEstado < 1 or request.nuevoEstado > 5:
            raise ValueError("Estado debe estar entre 1 y 5")

        if request.nuevoEstado == 4:
            if request.calificacion < 1 or request.calificacion > 5:
                raise ValueError("Calificación debe estar entre 1 y 5")

        function = contract.functions.cambiarEstadoServicio(
            tokenId, request.nuevoEstado, request.calificacion
        )

        tx_result = build_and_send_transaction(function)

        receipt = web3.eth.get_transaction_receipt(tx_result["transactionHash"])
        logs = contract.events.EstadoCambiado().process_receipt(receipt)

        estado_anterior = logs[0]["args"]["estadoAnterior"] if logs else None

        # Registrar transacción en el log
        log_transaction(
            tx_hash=tx_result["transactionHash"],
            function_name="cambiarEstadoServicio",
            parameters={
                "tokenId": tokenId,
                "nuevoEstado": request.nuevoEstado,
                "calificacion": request.calificacion,
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
            "nuevoEstado": request.nuevoEstado,
            "calificacion": request.calificacion,
            "transaction": tx_result,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== ENDPOINTS - 3. CONFIGURAR URIs ====================
@app.post("/configuracion/uri-estado")
async def configurar_uri_estado(request: ConfigurarURIRequest):
    """
    Configurar URI por Estado

    Configura la URI de metadatos para cada estado del servicio NFT.

    - **Gasta gas** - Transacción en blockchain
    - **Estados**: 1=CREADO, 2=ENCONTRADO, 3=TERMINADO, 4=CALIFICADO, 5=PAGADO
    - **URI dinámica**: Cada estado puede tener metadatos diferentes
    - **Retorna**: estado configurado, URI, información de transacción
    """
    try:
        if request.estado < 1 or request.estado > 5:
            raise ValueError("Estado debe estar entre 1 y 5")

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

        return {
            "success": True,
            "estado": request.estado,
            "uri": request.nuevaURI,
            "transaction": tx_result,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== ENDPOINTS - 4. CONSULTAS ====================
@app.get("/servicios/{tokenId}/estado")
async def obtener_estado_servicio(tokenId: int):
    """
    Obtener Estado del Servicio

    Consulta el estado actual de un servicio NFT.

    - **Sin gas** - Solo lectura
    - **Retorna**: estado numérico (1-5) y nombre del estado
    - **Estados**: 1=CREADO, 2=ENCONTRADO, 3=TERMINADO, 4=CALIFICADO, 5=PAGADO
    """
    try:
        estado = contract.functions.obtenerEstadoServicio(tokenId).call()
        estados_map = {
            1: "CREADO",
            2: "ENCONTRADO",
            3: "TERMINADO",
            4: "CALIFICADO",
            5: "PAGADO",
        }
        return {
            "tokenId": tokenId,
            "estado": estado,
            "estadoNombre": estados_map.get(estado, "DESCONOCIDO"),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/servicios/{tokenId}/uri")
async def obtener_uri_servicio(tokenId: int):
    """
    Obtener URI del Servicio

    Consulta la URI de metadatos actual del servicio NFT.

    - **Sin gas** - Solo lectura
    - **URI dinámica**: Cambia según el estado del servicio
    - **Retorna**: URI configurada para el estado actual
    """
    try:
        uri = contract.functions.obtenerURIServicio(tokenId).call()
        return {"tokenId": tokenId, "uri": uri}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/servicios/{tokenId}/calificacion")
async def obtener_calificacion_servicio(tokenId: int):
    """
    Obtener Calificación del Servicio

    Consulta la calificación asignada a un servicio.

    - **Sin gas** - Solo lectura
    - **Retorna**: calificación numérica (0-5)
    - **Nota**: Solo aplica en estado CALIFICADO (4), otros estados retornan 0
    """
    try:
        calificacion = contract.functions.obtenerCalificacionServicio(tokenId).call()
        return {"tokenId": tokenId, "calificacion": calificacion}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/servicios/{tokenId}/acompanante")
async def obtener_acompanante(tokenId: int):
    """
    Obtener Acompañante Asignado

    Consulta el acompañante asignado a un servicio.

    - **Sin gas** - Solo lectura
    - **Retorna**: dirección del acompañante asignado
    - **Requerido**: Para avanzar a estados ENCONTRADO y PAGADO
    """
    try:
        acompanante = contract.functions.obtenerAcompanante(tokenId).call()
        return {"tokenId": tokenId, "acompanante": acompanante}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/servicios/{tokenId}/evidencia")
async def obtener_evidencia_servicio(tokenId: int):
    """
    4e. Obtener el NFT de evidencia (se crea al pagar)
    """
    try:
        evidencia = contract.functions.obtenerEvidenciaServicio(tokenId).call()
        return {"tokenId": tokenId, "tokenIdEvidencia": evidencia}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/servicios/usuario/{usuarioAddress}")
async def obtener_servicios_usuario(usuarioAddress: str):
    """
    Listar Servicios por Usuario

    Obtiene todos los servicios NFT de una dirección específica.

    - **Sin gas** - Solo lectura
    - **Retorna**: lista de tokenIds que posee el usuario
    - **Incluye**: Servicios creados y NFTs de evidencia
    """
    try:
        usuario = Web3.to_checksum_address(usuarioAddress)
        balance = contract.functions.balanceOf(usuario).call()

        # Obtener el próximo token ID para saber el rango máximo
        next_token_id = contract.functions.obtenerProximoTokenId().call()

        servicios = []
        # Buscar todos los tokens que pertenecen al usuario
        for token_id in range(next_token_id):
            try:
                owner = contract.functions.ownerOf(token_id).call()
                if owner.lower() == usuario.lower():
                    servicios.append(token_id)
            except Exception:
                # Si ownerOf falla, el token no existe o fue quemado
                continue

        return {"usuario": usuario, "cantidad": balance, "servicios": servicios}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error al obtener servicios: {str(e)}"
        )


# ==================== ENDPOINTS ADICIONALES ====================
@app.post("/servicios/{tokenId}/asignar-acompanante")
async def asignar_acompanante(tokenId: int, request: AsignarAcompananteRequest):
    """
    Asignar Acompañante - Estado: ENCONTRADO (2)

    Asigna un acompañante a un servicio específico.
    Cambia el estado a ENCONTRADO (2) si estaba en CREADO (1).

    - **Gasta gas** - Transacción en blockchain
    - **Requerido para**: Avanzar a estados TERMINADO y PAGADO
    - **Retorna**: tokenId, acompañante, información de transacción
    """
    try:
        acompanante = Web3.to_checksum_address(request.acompanante)
        function = contract.functions.asignarAcompanante(tokenId, acompanante)

        tx_result = build_and_send_transaction(function)

        # Registrar transacción en el log
        log_transaction(
            tx_hash=tx_result["transactionHash"],
            function_name="asignarAcompanante",
            parameters={"tokenId": tokenId, "acompanante": acompanante},
            result={"tokenId": tokenId, **tx_result},
            status="success" if tx_result["status"] == 1 else "failed",
        )

        return {
            "success": True,
            "tokenId": tokenId,
            "acompanante": acompanante,
            "transaction": tx_result,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/servicios/{tokenId}/marcar-pagado")
async def marcar_como_pagado(tokenId: int):
    """
    Marcar como Pagado - Estado: PAGADO (5)

    Marca un servicio como pagado y crea automáticamente un NFT de evidencia.
    Solo funciona si el servicio está en estado CALIFICADO (4).

    - **Gasta gas** - Transacción en blockchain
    - **Crea NFT**: Genera automáticamente NFT de evidencia para el acompañante
    - **Retorna**: tokenId, tokenIdEvidencia, estado, información de transacción
    """
    try:
        function = contract.functions.marcarComoPagado(tokenId)

        tx_result = build_and_send_transaction(function)

        receipt = web3.eth.get_transaction_receipt(tx_result["transactionHash"])
        logs = contract.events.ServicioPagado().process_receipt(receipt)

        token_id_evidencia = logs[0]["args"]["tokenIdEvidencia"] if logs else None

        # Registrar transacción en el log
        log_transaction(
            tx_hash=tx_result["transactionHash"],
            function_name="marcarComoPagado",
            parameters={"tokenId": tokenId},
            result={
                "tokenId": tokenId,
                "tokenIdEvidencia": token_id_evidencia,
                **tx_result,
            },
            status="success" if tx_result["status"] == 1 else "failed",
        )

        return {
            "success": True,
            "tokenId": tokenId,
            "tokenIdEvidencia": token_id_evidencia,
            "transaction": tx_result,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/info/contrato")
async def obtener_info_contrato():
    """
    Información del Contrato

    Obtiene información básica del contrato NFT.

    - **Sin gas** - Solo lectura
    - **Retorna**: dirección, nombre, símbolo, próximo tokenId
    - **Contrato**: ColeccionServiciosNFT (CSNFT)
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
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/info/cuenta")
async def obtener_info_cuenta():
    """
    Información de Cuenta Ejecutora

    Obtiene información de la cuenta que ejecuta las transacciones.

    - **Sin gas** - Solo lectura
    - **Retorna**: dirección y balance en ETH/Wei
    - **Usada para**: Firmar y enviar transacciones
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

    Verifica el estado de la API y la conexión a la red blockchain.

    - **Sin gas** - Solo lectura
    - **Retorna**: estado de salud, conectividad, número de bloque actual
    - **Estados**: healthy (conectado), disconnected (sin conexión)
    """
    try:
        is_connected = web3.is_connected()
        block_number = web3.eth.block_number if is_connected else None

        return {
            "status": "healthy" if is_connected else "disconnected",
            "connected": is_connected,
            "blockNumber": block_number,
            "chainId": CHAIN_ID,
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ==================== ENDPOINTS DE LOGS ====================
@app.get("/logs/transacciones")
async def obtener_logs_transacciones(limit: int = 50):
    """
    Historial de Transacciones

    Obtiene el historial completo de transacciones ejecutadas por el backend.

    - **Sin gas** - Solo lectura
    - **Parámetros**: limit (opcional) - número máximo de transacciones a retornar
    - **Retorna**: lista de transacciones con detalles completos
    - **Incluye**: hash, función, parámetros, resultado, gas usado
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

    Obtiene estadísticas agregadas de todas las transacciones registradas.

    - **Sin gas** - Solo lectura
    - **Retorna**: total de transacciones, conteos por función, gas total usado
    - **Métricas**: éxito/error, funciones más usadas, fechas de primera/última transacción
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

    Busca una transacción específica en el registro usando su hash.

    - **Sin gas** - Solo lectura
    - **Parámetros**: hash de transacción
    - **Retorna**: detalles completos de la transacción específica
    """
    try:
        from transaction_logger import transaction_logger

        transaction = transaction_logger.get_transaction_by_hash(tx_hash)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error buscando transacción: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
