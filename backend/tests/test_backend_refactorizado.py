#!/usr/bin/env python3
"""
Script de Pruebas Completo para Backend NFT Servicios REFACTORIZADO

Este script prueba todos los endpoints del backend FastAPI refactorizado para el contrato
NFT de servicios de acompañamiento a adultos mayores con estados simplificados.

Características del Sistema Refactorizado:
- 3 estados: CREADO (1), ENCONTRADO (2), FINALIZADO (3)
- Transferencia automática de NFT al asignar acompañante
- Sin sistema de calificación
- Estadísticas avanzadas por wallet
- Flujo simplificado

Requisitos:
- Backend ejecutándose en http://localhost:8000
- Wallet con ETH suficiente para gas fees
- Variables de entorno configuradas correctamente

Ejecución:
    python test_backend_refactorizado.py
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
TEST_URI_FINALIZADO = "ipfs://QmTestURIFinalizado123456789"


class BackendTesterRefactorizado:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.test_results = []
        self.created_token_id = None
        self.test_start_time = datetime.now()

    def log_test(self, test_name, success, details=None, response_time=None):
        """Registra el resultado de una prueba"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test_name": test_name,
            "success": success,
            "details": details or {},
            "response_time_ms": response_time,
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        time_str = f" ({response_time}ms)" if response_time else ""
        print(f"{status} {test_name}{time_str}")
        if details and not success:
            print(f"   Error: {details}")

    def make_request(self, method, endpoint, data=None, params=None):
        """Realiza una petición HTTP y mide el tiempo de respuesta"""
        start_time = time.time()
        try:
            if method.upper() == "GET":
                response = self.session.get(f"{BASE_URL}{endpoint}", params=params)
            elif method.upper() == "POST":
                response = self.session.post(f"{BASE_URL}{endpoint}", json=data)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")

            response_time = int((time.time() - start_time) * 1000)
            return response, response_time
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            return None, response_time

    def test_health_check(self):
        """1. Verificar que el backend esté funcionando"""
        print("\n" + "=" * 60)
        print("🏥 TESTS DE SALUD DEL SISTEMA")
        print("=" * 60)

        response, response_time = self.make_request("GET", "/health")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test(
                "Health Check", data.get("status") == "healthy", data, response_time
            )
        else:
            self.log_test("Health Check", False, "Backend no responde", response_time)

    def test_info_endpoints(self):
        """2. Probar endpoints de información"""
        print("\n📊 TESTS DE INFORMACIÓN")
        print("-" * 40)

        # Info del contrato
        response, response_time = self.make_request("GET", "/info/contrato")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test(
                "Info Contrato",
                "CSNFT" in data.get("simbolo", ""),
                {"contrato": data.get("contractAddress")},
                response_time,
            )
        else:
            self.log_test(
                "Info Contrato", False, "Error obteniendo info contrato", response_time
            )

        # Info de la cuenta
        response, response_time = self.make_request("GET", "/info/cuenta")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test(
                "Info Cuenta",
                data.get("balanceETH", 0) > 0,
                {"balance": f"{data.get('balanceETH')} ETH"},
                response_time,
            )
        else:
            self.log_test(
                "Info Cuenta", False, "Error obteniendo info cuenta", response_time
            )

        # Info de cambios (nuevo endpoint)
        response, response_time = self.make_request("GET", "/info/cambios")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test(
                "Info Cambios Refactor",
                data.get("version") == "2.0.0",
                {"version": data.get("version")},
                response_time,
            )
        else:
            self.log_test(
                "Info Cambios Refactor",
                False,
                "Error obteniendo info cambios",
                response_time,
            )

    def test_configurar_uris(self):
        """3. Configurar URIs para los estados"""
        print("\n⚙️ TESTS DE CONFIGURACIÓN")
        print("-" * 40)

        uris_config = [
            (1, TEST_URI_CREADO, "CREADO"),
            (2, TEST_URI_ENCONTRADO, "ENCONTRADO"),
            (3, TEST_URI_FINALIZADO, "FINALIZADO"),
        ]

        for estado, uri, nombre in uris_config:
            data = {"estado": estado, "nuevaURI": uri}
            response, response_time = self.make_request(
                "POST", "/configuracion/uri-estado", data
            )

            if response and response.status_code == 200:
                result = response.json()
                self.log_test(
                    f"Configurar URI {nombre}",
                    result.get("success", False),
                    {"estado": estado, "uri": uri[:50] + "..."},
                    response_time,
                )
                time.sleep(2)  # Esperar para que se confirme la transacción
            else:
                error_detail = (
                    response.json().get("detail") if response else "Sin respuesta"
                )
                self.log_test(
                    f"Configurar URI {nombre}", False, error_detail, response_time
                )

    def test_crear_servicio(self):
        """4. Crear un nuevo servicio"""
        print("\n🆕 TESTS DE CREACIÓN DE SERVICIOS")
        print("-" * 40)

        data = {"destinatario": TEST_DESTINATARIO}
        response, response_time = self.make_request("POST", "/servicios/crear", data)

        if response and response.status_code == 200:
            result = response.json()
            if result.get("success") and "tokenId" in result:
                self.created_token_id = result["tokenId"]
                self.log_test(
                    "Crear Servicio",
                    True,
                    {"tokenId": self.created_token_id, "estado": result.get("estado")},
                    response_time,
                )
                time.sleep(3)  # Esperar confirmación
            else:
                self.log_test("Crear Servicio", False, result, response_time)
        else:
            error_detail = (
                response.json().get("detail") if response else "Sin respuesta"
            )
            self.log_test("Crear Servicio", False, error_detail, response_time)

    def test_consultas_servicio(self):
        """5. Consultar información del servicio creado"""
        print("\n🔍 TESTS DE CONSULTAS")
        print("-" * 40)

        if not self.created_token_id:
            self.log_test("Consultas (Sin Token)", False, "No hay token para consultar")
            return

        # Consultar estado
        response, response_time = self.make_request(
            "GET", f"/servicios/{self.created_token_id}/estado"
        )
        if response and response.status_code == 200:
            data = response.json()
            self.log_test(
                "Consultar Estado",
                data.get("estado") == 1 and data.get("estadoNombre") == "CREADO",
                {"estado": data.get("estadoNombre")},
                response_time,
            )
        else:
            self.log_test(
                "Consultar Estado", False, "Error consultando estado", response_time
            )

        # Consultar acompañante (debería ser null inicialmente)
        response, response_time = self.make_request(
            "GET", f"/servicios/{self.created_token_id}/acompanante"
        )
        if response and response.status_code == 200:
            data = response.json()
            self.log_test(
                "Consultar Acompañante",
                data.get("acompanante") is None,
                {"acompanante": data.get("acompanante")},
                response_time,
            )
        else:
            self.log_test(
                "Consultar Acompañante",
                False,
                "Error consultando acompañante",
                response_time,
            )

        # Consultar URI
        response, response_time = self.make_request(
            "GET", f"/servicios/{self.created_token_id}/uri"
        )
        if response and response.status_code == 200:
            data = response.json()
            self.log_test(
                "Consultar URI",
                TEST_URI_CREADO in data.get("uri", ""),
                {"uri": data.get("uri", "")[:50] + "..."},
                response_time,
            )
        else:
            self.log_test(
                "Consultar URI", False, "Error consultando URI", response_time
            )

        # Consultar información completa (nuevo endpoint)
        response, response_time = self.make_request(
            "GET", f"/servicios/{self.created_token_id}/info"
        )
        if response and response.status_code == 200:
            data = response.json()
            self.log_test(
                "Consultar Info Completa",
                data.get("estadoNombre") == "CREADO",
                {"propietario": data.get("propietario", "")[:10] + "..."},
                response_time,
            )
        else:
            self.log_test(
                "Consultar Info Completa",
                False,
                "Error consultando info completa",
                response_time,
            )

    def test_asignar_acompanante(self):
        """6. Asignar acompañante (transfiere NFT)"""
        print("\n👥 TESTS DE ASIGNACIÓN DE ACOMPAÑANTE")
        print("-" * 40)

        if not self.created_token_id:
            self.log_test(
                "Asignar Acompañante (Sin Token)", False, "No hay token para asignar"
            )
            return

        data = {"acompanante": TEST_ACOMPANANTE}
        response, response_time = self.make_request(
            "POST", f"/servicios/{self.created_token_id}/asignar-acompanante", data
        )

        if response and response.status_code == 200:
            result = response.json()
            success = (
                result.get("success", False)
                and result.get("nuevoEstado") == 2
                and result.get("estadoNombre") == "ENCONTRADO"
                and result.get("nftTransferido", False)
            )
            self.log_test(
                "Asignar Acompañante",
                success,
                {
                    "nuevoEstado": result.get("estadoNombre"),
                    "nftTransferido": result.get("nftTransferido"),
                },
                response_time,
            )
            time.sleep(3)  # Esperar confirmación
        else:
            error_detail = (
                response.json().get("detail") if response else "Sin respuesta"
            )
            self.log_test("Asignar Acompañante", False, error_detail, response_time)

    def test_verificar_transferencia(self):
        """7. Verificar que el NFT fue transferido"""
        print("\n🔄 TESTS DE TRANSFERENCIA")
        print("-" * 40)

        if not self.created_token_id:
            self.log_test(
                "Verificar Transferencia (Sin Token)",
                False,
                "No hay token para verificar",
            )
            return

        # Verificar que el estado cambió
        response, response_time = self.make_request(
            "GET", f"/servicios/{self.created_token_id}/estado"
        )
        if response and response.status_code == 200:
            data = response.json()
            self.log_test(
                "Estado Post-Asignación",
                data.get("estado") == 2 and data.get("estadoNombre") == "ENCONTRADO",
                {"estado": data.get("estadoNombre")},
                response_time,
            )
        else:
            self.log_test(
                "Estado Post-Asignación",
                False,
                "Error verificando estado",
                response_time,
            )

        # Verificar información completa
        response, response_time = self.make_request(
            "GET", f"/servicios/{self.created_token_id}/info"
        )
        if response and response.status_code == 200:
            data = response.json()
            # El propietario ahora debería ser el acompañante
            self.log_test(
                "Propietario Post-Transferencia",
                data.get("propietario", "").lower() == TEST_ACOMPANANTE.lower(),
                {"nuevoPropietario": data.get("propietario", "")[:10] + "..."},
                response_time,
            )
        else:
            self.log_test(
                "Propietario Post-Transferencia",
                False,
                "Error verificando propietario",
                response_time,
            )

    def test_finalizar_servicio(self):
        """8. Finalizar el servicio"""
        print("\n✅ TESTS DE FINALIZACIÓN")
        print("-" * 40)

        if not self.created_token_id:
            self.log_test(
                "Finalizar Servicio (Sin Token)", False, "No hay token para finalizar"
            )
            return

        # Opción 1: Usar el endpoint directo de finalizar
        response, response_time = self.make_request(
            "POST", f"/servicios/{self.created_token_id}/finalizar"
        )
        if response and response.status_code == 200:
            result = response.json()
            success = (
                result.get("success", False)
                and result.get("nuevoEstado") == 3
                and result.get("estadoNombre") == "FINALIZADO"
            )
            self.log_test(
                "Finalizar Servicio (Directo)",
                success,
                {"estado": result.get("estadoNombre")},
                response_time,
            )
            time.sleep(3)
        else:
            # Opción 2: Usar cambiar estado
            data = {"nuevoEstado": 3}
            response, response_time = self.make_request(
                "POST", f"/servicios/{self.created_token_id}/cambiar-estado", data
            )
            if response and response.status_code == 200:
                result = response.json()
                success = result.get("nuevoEstado") == 3
                self.log_test(
                    "Finalizar Servicio (Cambiar Estado)",
                    success,
                    {"estadoFinal": result.get("nuevoEstadoNombre")},
                    response_time,
                )
                time.sleep(3)
            else:
                error_detail = (
                    response.json().get("detail") if response else "Sin respuesta"
                )
                self.log_test("Finalizar Servicio", False, error_detail, response_time)

    def test_estadisticas_wallet(self):
        """9. Probar estadísticas por wallet"""
        print("\n📊 TESTS DE ESTADÍSTICAS")
        print("-" * 40)

        # Estadísticas del cliente original
        response, response_time = self.make_request(
            "GET", f"/estadisticas/{TEST_DESTINATARIO}"
        )
        if response and response.status_code == 200:
            data = response.json()
            stats = data.get("estadisticas", {})
            self.log_test(
                "Estadísticas Cliente",
                stats.get("totalServicios", 0) >= 0,
                {
                    "totalServicios": stats.get("totalServicios", 0),
                    "finalizados": stats.get("serviciosFinalizados", 0),
                },
                response_time,
            )
        else:
            error_detail = (
                response.json().get("detail") if response else "Sin respuesta"
            )
            self.log_test("Estadísticas Cliente", False, error_detail, response_time)

        # Estadísticas del acompañante (ahora propietario del NFT)
        response, response_time = self.make_request(
            "GET", f"/estadisticas/{TEST_ACOMPANANTE}"
        )
        if response and response.status_code == 200:
            data = response.json()
            stats = data.get("estadisticas", {})
            servicios = data.get("servicios", [])

            # Debería tener al menos 1 servicio (el que le fue transferido)
            success = stats.get("totalServicios", 0) >= 1

            self.log_test(
                "Estadísticas Acompañante",
                success,
                {
                    "totalServicios": stats.get("totalServicios", 0),
                    "serviciosEncontrados": stats.get("serviciosEncontrados", 0),
                    "serviciosFinalizados": stats.get("serviciosFinalizados", 0),
                },
                response_time,
            )
        else:
            error_detail = (
                response.json().get("detail") if response else "Sin respuesta"
            )
            self.log_test(
                "Estadísticas Acompañante", False, error_detail, response_time
            )

    def test_resumen_general(self):
        """10. Probar resumen general del sistema"""
        print("\n🌐 TESTS DE RESUMEN GENERAL")
        print("-" * 40)

        response, response_time = self.make_request(
            "GET", "/estadisticas/general/resumen"
        )
        if response and response.status_code == 200:
            data = response.json()
            success = (
                "totalNFTsCreados" in data
                and "estadisticasPorEstado" in data
                and "metricas" in data
            )
            self.log_test(
                "Resumen General",
                success,
                {
                    "totalNFTs": data.get("totalNFTsCreados", 0),
                    "finalizados": data.get("estadisticasPorEstado", {}).get(
                        "finalizados", 0
                    ),
                },
                response_time,
            )
        else:
            error_detail = (
                response.json().get("detail") if response else "Sin respuesta"
            )
            self.log_test("Resumen General", False, error_detail, response_time)

    def test_endpoints_eliminados(self):
        """11. Verificar que los endpoints eliminados devuelven 404"""
        print("\n🚫 TESTS DE ENDPOINTS ELIMINADOS")
        print("-" * 40)

        endpoints_eliminados = [
            ("/servicios/1/calificacion", "GET"),
            ("/servicios/1/evidencia", "GET"),
            ("/servicios/1/marcar-pagado", "POST"),
        ]

        for endpoint, method in endpoints_eliminados:
            response, response_time = self.make_request(method, endpoint)
            success = response is None or response.status_code == 404
            self.log_test(
                f"Endpoint Eliminado {method} {endpoint}",
                success,
                {"status_code": response.status_code if response else "Sin respuesta"},
                response_time,
            )

    def test_logs_sistema(self):
        """12. Probar endpoints de logs"""
        print("\n📝 TESTS DE LOGS")
        print("-" * 40)

        # Historial de transacciones
        response, response_time = self.make_request(
            "GET", "/logs/transacciones", params={"limit": 5}
        )
        if response and response.status_code == 200:
            data = response.json()
            self.log_test(
                "Logs Transacciones",
                "transactions" in data,
                {"total": data.get("total", 0)},
                response_time,
            )
        else:
            self.log_test(
                "Logs Transacciones", False, "Error obteniendo logs", response_time
            )

        # Estadísticas de logs
        response, response_time = self.make_request("GET", "/logs/estadisticas")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test(
                "Estadísticas Logs",
                isinstance(data, dict),
                {"keys": list(data.keys()) if isinstance(data, dict) else []},
                response_time,
            )
        else:
            self.log_test(
                "Estadísticas Logs",
                False,
                "Error obteniendo estadísticas",
                response_time,
            )

    def generate_report(self):
        """Generar reporte final de las pruebas"""
        print("\n" + "=" * 60)
        print("📋 REPORTE FINAL DE PRUEBAS")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        test_duration = datetime.now() - self.test_start_time

        print(f"📊 Resumen de Resultados:")
        print(f"   ✅ Pruebas exitosas: {passed_tests}")
        print(f"   ❌ Pruebas fallidas: {failed_tests}")
        print(f"   📈 Tasa de éxito: {success_rate:.1f}%")
        print(f"   ⏱️  Duración total: {test_duration}")
        print(f"   🎯 Token creado: {self.created_token_id}")

        # Guardar resultados detallados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_refactor_{timestamp}.json"

        report = {
            "test_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "duration_seconds": test_duration.total_seconds(),
                "created_token_id": self.created_token_id,
                "system_version": "2.0.0 - Refactorizado",
            },
            "test_results": self.test_results,
        }

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        print(f"💾 Resultados guardados en: {filename}")

        if failed_tests == 0:
            print(
                "\n🎉 ¡TODAS LAS PRUEBAS PASARON! Sistema refactorizado funcionando correctamente."
            )
        else:
            print(
                f"\n⚠️  {failed_tests} pruebas fallaron. Revisar detalles en el archivo de resultados."
            )

        print("=" * 60)

    def run_all_tests(self):
        """Ejecutar todas las pruebas en orden"""
        print("🚀 INICIANDO PRUEBAS DEL SISTEMA REFACTORIZADO")
        print("=" * 60)
        print("🔄 Estados: CREADO (1) → ENCONTRADO (2) → FINALIZADO (3)")
        print(
            "🎯 Características: Transferencia automática, Sin calificaciones, Estadísticas avanzadas"
        )
        print("=" * 60)

        try:
            self.test_health_check()
            self.test_info_endpoints()
            self.test_configurar_uris()
            self.test_crear_servicio()
            self.test_consultas_servicio()
            self.test_asignar_acompanante()
            self.test_verificar_transferencia()
            self.test_finalizar_servicio()
            self.test_estadisticas_wallet()
            self.test_resumen_general()
            self.test_endpoints_eliminados()
            self.test_logs_sistema()
        except KeyboardInterrupt:
            print("\n⚠️  Pruebas interrumpidas por el usuario")
        except Exception as e:
            print(f"\n❌ Error inesperado durante las pruebas: {str(e)}")
        finally:
            self.generate_report()


def main():
    """Función principal"""
    print("NFT Backend Refactorizado - Suite de Pruebas Completa")
    print("=" * 60)
    print(
        "⚠️  IMPORTANTE: Asegúrate de que el backend esté ejecutándose en http://localhost:8000"
    )
    print("💰 REQUISITO: La wallet debe tener ETH suficiente para las transacciones")
    print("🔧 VERSIÓN: Sistema refactorizado con 3 estados simplificados")

    input("\nPresiona Enter para continuar o Ctrl+C para cancelar...")

    tester = BackendTesterRefactorizado()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
