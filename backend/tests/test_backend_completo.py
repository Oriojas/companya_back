#!/usr/bin/env python3
"""
Script de Pruebas Completo para Backend NFT Servicios

Este script prueba todos los endpoints del backend FastAPI para el contrato
NFT de servicios de acompañamiento a adultos mayores.

Características:
- Prueba todos los endpoints documentados en BACKEND_README.md
- Flujo completo de creación y gestión de un servicio
- Manejo de errores y validaciones
- Logging detallado de resultados
- Compatible con Arbitrum Sepolia

Requisitos:
- Backend ejecutándose en http://localhost:8000
- Wallet con ETH suficiente para gas fees
- Variables de entorno configuradas correctamente

Ejecución:
    python test_backend_completo.py
"""

import json
import sys
import time
from datetime import datetime

import requests

# Configuración
BASE_URL = "http://localhost:8000"
TEST_DESTINATARIO = "0xa92d504731aA3E99DF20ffd200ED03F9a55a6219"
TEST_ACOMPANANTE = "0x742d35Cc6634C0532925a3b8D4B6A5F6C6D5B7C8"
TEST_URI_CREADO = "ipfs://QmTestURICreado123456789"
TEST_URI_ENCONTRADO = "ipfs://QmTestURIEncontrado123456789"


class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.test_results = []
        self.created_token_id = None
        self.evidence_token_id = None

    def log_test(self, test_name, success, details=None):
        """Registra el resultado de una prueba"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "success": success,
            "details": details,
        }
        self.test_results.append(result)

        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"{timestamp} - {status}: {test_name}")
        if details and not success:
            print(f"   Detalles: {details}")

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Realiza una petición HTTP con manejo de errores"""
        url = f"{BASE_URL}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")

            if response.status_code == expected_status:
                return response.json()
            else:
                return {
                    "error": f"Status code {response.status_code}",
                    "response": response.text,
                }

        except requests.exceptions.ConnectionError:
            return {"error": "No se puede conectar al backend. ¿Está ejecutándose?"}
        except requests.exceptions.Timeout:
            return {"error": "Timeout en la conexión"}
        except Exception as e:
            return {"error": f"Error inesperado: {str(e)}"}

    def test_health_check(self):
        """Prueba el endpoint de health check"""
        result = self.make_request("GET", "/health")
        success = result.get("status") == "healthy" and result.get("connected") is True
        self.log_test("Health Check", success, result)
        return success

    def test_info_contrato(self):
        """Prueba la información del contrato"""
        result = self.make_request("GET", "/info/contrato")
        success = (
            result.get("contractAddress") is not None
            and result.get("nombre") == "ColeccionServiciosNFT"
            and result.get("chainId") == 421614
        )
        self.log_test("Información del Contrato", success, result)
        return success

    def test_info_cuenta(self):
        """Prueba la información de la cuenta ejecutora"""
        result = self.make_request("GET", "/info/cuenta")
        success = (
            result.get("address") is not None
            and result.get("balanceETH") is not None
            and float(result.get("balanceETH", 0)) > 0
        )
        self.log_test("Información de Cuenta", success, result)
        return success

    def test_configurar_uri_estado(self):
        """Prueba configurar URI para estado CREADO"""
        data = {"estado": 1, "nuevaURI": TEST_URI_CREADO}
        result = self.make_request("POST", "/configuracion/uri-estado", data)
        success = result.get("success") is True and result.get("uri") == TEST_URI_CREADO
        self.log_test("Configurar URI Estado CREADO", success, result)

        # Configurar también URI para estado ENCONTRADO
        data = {"estado": 2, "nuevaURI": TEST_URI_ENCONTRADO}
        result = self.make_request("POST", "/configuracion/uri-estado", data)
        success = result.get("success") is True
        self.log_test("Configurar URI Estado ENCONTRADO", success, result)

        return success

    def test_crear_servicio(self):
        """Prueba crear un nuevo servicio"""
        data = {"destinatario": TEST_DESTINATARIO}
        result = self.make_request("POST", "/servicios/crear", data)

        success = (
            result.get("success") is True
            and result.get("tokenId") is not None
            and result.get("estado") == 1
        )

        if success:
            self.created_token_id = result["tokenId"]
            self.log_test(
                "Crear Servicio", success, f"Token ID creado: {self.created_token_id}"
            )
        else:
            self.log_test("Crear Servicio", success, result)

        return success

    def test_obtener_estado_servicio(self):
        """Prueba obtener estado del servicio creado"""
        if not self.created_token_id:
            self.log_test("Obtener Estado Servicio", False, "No hay token ID creado")
            return False

        result = self.make_request("GET", f"/servicios/{self.created_token_id}/estado")
        success = (
            result.get("tokenId") == self.created_token_id
            and result.get("estado") == 1
            and result.get("estadoNombre") == "CREADO"
        )
        self.log_test("Obtener Estado Servicio", success, result)
        return success

    def test_obtener_uri_servicio(self):
        """Prueba obtener URI del servicio"""
        if not self.created_token_id:
            self.log_test("Obtener URI Servicio", False, "No hay token ID creado")
            return False

        result = self.make_request("GET", f"/servicios/{self.created_token_id}/uri")
        success = (
            result.get("tokenId") == self.created_token_id
            and result.get("uri") is not None
        )
        self.log_test("Obtener URI Servicio", success, result)
        return success

    def test_asignar_acompanante(self):
        """Prueba asignar acompañante al servicio"""
        if not self.created_token_id:
            self.log_test("Asignar Acompañante", False, "No hay token ID creado")
            return False

        data = {"tokenId": self.created_token_id, "acompanante": TEST_ACOMPANANTE}
        result = self.make_request(
            "POST", f"/servicios/{self.created_token_id}/asignar-acompanante", data
        )
        success = (
            result.get("success") is True
            and result.get("acompanante", "").lower() == TEST_ACOMPANANTE.lower()
        )
        # print(f"DEBUG - Asignar Acompañante: success={success}, result={result}")
        self.log_test("Asignar Acompañante", success, result)
        return success

    def test_obtener_acompanante(self):
        """Prueba obtener acompañante asignado"""
        if not self.created_token_id:
            self.log_test("Obtener Acompañante", False, "No hay token ID creado")
            return False

        result = self.make_request(
            "GET", f"/servicios/{self.created_token_id}/acompanante"
        )
        success = (
            result.get("tokenId") == self.created_token_id
            and result.get("acompanante", "").lower() == TEST_ACOMPANANTE.lower()
        )
        # print(f"DEBUG - Obtener Acompañante: success={success}, result={result}")
        self.log_test("Obtener Acompañante", success, result)
        return success

    def test_cambiar_estado_encontrado(self):
        """Prueba cambiar estado a ENCONTRADO"""
        if not self.created_token_id:
            self.log_test(
                "Cambiar Estado a ENCONTRADO", False, "No hay token ID creado"
            )
            return False

        data = {"nuevoEstado": 2, "calificacion": 0}
        result = self.make_request(
            "POST", f"/servicios/{self.created_token_id}/cambiar-estado", data
        )
        success = (
            result.get("success") is True
            and result.get("nuevoEstado") == 2
            and result.get("estadoAnterior") == 1
        )
        self.log_test("Cambiar Estado a ENCONTRADO", success, result)
        return success

    def test_cambiar_estado_terminado(self):
        """Prueba cambiar estado a TERMINADO"""
        if not self.created_token_id:
            self.log_test("Cambiar Estado a TERMINADO", False, "No hay token ID creado")
            return False

        data = {"nuevoEstado": 3, "calificacion": 0}
        result = self.make_request(
            "POST", f"/servicios/{self.created_token_id}/cambiar-estado", data
        )
        success = (
            result.get("success") is True
            and result.get("nuevoEstado") == 3
            and result.get("estadoAnterior") == 2
        )
        self.log_test("Cambiar Estado a TERMINADO", success, result)
        return success

    def test_cambiar_estado_calificado(self):
        """Prueba cambiar estado a CALIFICADO con calificación"""
        if not self.created_token_id:
            self.log_test(
                "Cambiar Estado a CALIFICADO", False, "No hay token ID creado"
            )
            return False

        data = {"nuevoEstado": 4, "calificacion": 5}
        result = self.make_request(
            "POST", f"/servicios/{self.created_token_id}/cambiar-estado", data
        )
        success = (
            result.get("success") is True
            and result.get("nuevoEstado") == 4
            and result.get("estadoAnterior") == 3
            and result.get("calificacion") == 5
        )
        self.log_test("Cambiar Estado a CALIFICADO", success, result)
        return success

    def test_obtener_calificacion_servicio(self):
        """Prueba obtener calificación del servicio"""
        if not self.created_token_id:
            self.log_test(
                "Obtener Calificación Servicio", False, "No hay token ID creado"
            )
            return False

        result = self.make_request(
            "GET", f"/servicios/{self.created_token_id}/calificacion"
        )
        success = (
            result.get("tokenId") == self.created_token_id
            and result.get("calificacion") == 5
        )
        self.log_test("Obtener Calificación Servicio", success, result)
        return success

    def test_marcar_como_pagado(self):
        """Prueba marcar servicio como pagado"""
        if not self.created_token_id:
            self.log_test("Marcar como Pagado", False, "No hay token ID creado")
            return False

        # Primero verificar que el servicio está en estado CALIFICADO (4)
        estado_result = self.make_request(
            "GET", f"/servicios/{self.created_token_id}/estado"
        )
        if estado_result.get("estado") != 4:
            self.log_test(
                "Marcar como Pagado",
                False,
                f"Servicio no está en estado CALIFICADO (4), está en estado {estado_result.get('estado')}",
            )
            return False

        result = self.make_request(
            "POST", f"/servicios/{self.created_token_id}/marcar-pagado"
        )
        success = (
            result.get("success") is True and result.get("tokenIdEvidencia") is not None
        )
        # print(f"DEBUG - Marcar como Pagado: success={success}, result={result}")

        if success:
            self.evidence_token_id = result["tokenIdEvidencia"]
            self.log_test(
                "Marcar como Pagado",
                success,
                f"Token ID evidencia: {self.evidence_token_id}",
            )
        else:
            self.log_test("Marcar como Pagado", success, result)

        return success

    def test_obtener_evidencia_servicio(self):
        """Prueba obtener NFT de evidencia"""
        if not self.created_token_id:
            self.log_test("Obtener Evidencia Servicio", False, "No hay token ID creado")
            return False

        result = self.make_request(
            "GET", f"/servicios/{self.created_token_id}/evidencia"
        )
        success = (
            result.get("tokenId") == self.created_token_id
            and result.get("tokenIdEvidencia") == self.evidence_token_id
        )
        # print(
        #     f"DEBUG - Obtener Evidencia: success={success}, result={result}, evidence_token_id={self.evidence_token_id}"
        # )
        self.log_test("Obtener Evidencia Servicio", success, result)
        return success

    def test_obtener_servicios_usuario(self):
        """Prueba listar servicios por usuario"""
        result = self.make_request("GET", f"/servicios/usuario/{TEST_DESTINATARIO}")
        success = (
            result.get("usuario") == TEST_DESTINATARIO
            and result.get("cantidad") is not None
            and isinstance(result.get("servicios"), list)
        )
        self.log_test("Obtener Servicios por Usuario", success, result)
        return success

    def test_obtener_logs_transacciones(self):
        """Prueba obtener logs de transacciones"""
        result = self.make_request("GET", "/logs/transacciones?limit=10")
        success = result.get("total") is not None and isinstance(
            result.get("transactions"), list
        )
        self.log_test("Obtener Logs de Transacciones", success, result)
        return success

    def test_obtener_estadisticas_logs(self):
        """Prueba obtener estadísticas de logs"""
        result = self.make_request("GET", "/logs/estadisticas")
        success = (
            result.get("total_transactions") is not None
            and result.get("function_counts") is not None
        )
        self.log_test("Obtener Estadísticas de Logs", success, result)
        return success

    def run_all_tests(self):
        """Ejecuta todas las pruebas en secuencia"""
        print("🚀 INICIANDO PRUEBAS COMPLETAS DEL BACKEND NFT SERVICIOS")
        print("=" * 60)

        # Pruebas de información básica
        self.test_health_check()
        self.test_info_contrato()
        self.test_info_cuenta()

        # Configuración inicial
        self.test_configurar_uri_estado()

        # Flujo completo del servicio
        self.test_crear_servicio()

        if self.created_token_id:
            # Pruebas de consulta
            self.test_obtener_estado_servicio()
            self.test_obtener_uri_servicio()

            # Gestión del servicio
            self.test_asignar_acompanante()
            self.test_obtener_acompanante()

            # Cambios de estado progresivos
            self.test_cambiar_estado_encontrado()
            self.test_cambiar_estado_terminado()
            self.test_cambiar_estado_calificado()
            self.test_obtener_calificacion_servicio()
            self.test_marcar_como_pagado()
            self.test_obtener_evidencia_servicio()

            # Consultas adicionales
            self.test_obtener_servicios_usuario()

        # Pruebas de logs
        self.test_obtener_logs_transacciones()
        self.test_obtener_estadisticas_logs()

        # Resumen final
        self.print_summary()

    def print_summary(self):
        """Imprime un resumen de los resultados"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        print(f"Total de pruebas: {total_tests}")
        print(f"Pruebas exitosas: {passed_tests}")
        print(f"Pruebas fallidas: {failed_tests}")
        print(f"Tasa de éxito: {(passed_tests / total_tests) * 100:.1f}%")

        if failed_tests > 0:
            print("\n❌ Pruebas fallidas:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}")

        if self.created_token_id:
            print(f"\n📝 Token ID del servicio de prueba: {self.created_token_id}")
        if self.evidence_token_id:
            print(f"📝 Token ID de evidencia creado: {self.evidence_token_id}")

        # Guardar resultados en archivo
        self.save_results_to_file()

    def save_results_to_file(self):
        """Guarda los resultados en un archivo JSON"""
        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "test_destinatario": TEST_DESTINATARIO,
            "test_acompanante": TEST_ACOMPANANTE,
            "created_token_id": self.created_token_id,
            "evidence_token_id": self.evidence_token_id,
            "results": self.test_results,
        }

        with open(filename, "w") as f:
            json.dump(results_data, f, indent=2)

        print(f"\n📁 Resultados guardados en: {filename}")


def main():
    """Función principal"""
    try:
        tester = BackendTester()
        tester.run_all_tests()

        # Verificar si hay fallas críticas
        failed_tests = sum(1 for result in tester.test_results if not result["success"])
        if failed_tests > 0:
            sys.exit(1)  # Exit con código de error si hay fallas
        else:
            print("\n🎉 ¡Todas las pruebas fueron exitosas!")

    except KeyboardInterrupt:
        print("\n⏹️  Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
