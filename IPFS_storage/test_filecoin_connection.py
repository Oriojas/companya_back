#!/usr/bin/env python3
"""
Test script for Filecoin connection with improved timeout and retry logic
This script tests the connection to multiple Filecoin RPC endpoints
"""

import os
import sys
import time
from datetime import datetime

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from filecoin_direct_client import FilecoinDirectClient


def test_filecoin_connection():
    """Test Filecoin connection with detailed reporting"""
    print("=" * 60)
    print("🚀 PRUEBA DE CONEXIÓN FILECOIN")
    print("=" * 60)

    # Set up test environment
    if not os.getenv("FILECOIN_PRIVATE_KEY"):
        print("⚠️  FILECOIN_PRIVATE_KEY not found in environment")
        print("💡 Setting test key for connection testing...")
        os.environ["FILECOIN_PRIVATE_KEY"] = "test_key_for_connection_testing"

    try:
        # Initialize client
        print("\n📡 Inicializando cliente Filecoin...")
        client = FilecoinDirectClient()

        print(f"✅ Cliente inicializado correctamente")
        print(f"   • RPC URL principal: {client.rpc_url}")
        print(f"   • URLs disponibles: {len(client.rpc_urls)}")
        print(f"   • Timeout: {client.timeout} segundos")
        print(f"   • Reintentos máximos: {client.max_retries}")

        # Test connection to each RPC endpoint
        print(f"\n🔗 Probando conexión a {len(client.rpc_urls)} endpoints...")

        working_endpoints = []
        failed_endpoints = []

        for i, url in enumerate(client.rpc_urls):
            print(f"\n   [{i + 1}/{len(client.rpc_urls)}] Probando: {url}")

            # Temporarily set this as the active URL
            original_url = client.rpc_url
            client.rpc_url = url

            try:
                start_time = time.time()

                # Test basic RPC call
                payload = {
                    "jsonrpc": "2.0",
                    "method": "Filecoin.ChainHead",
                    "params": [],
                    "id": 1,
                }

                result = client._make_rpc_request(payload)
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms

                if result and "result" in result:
                    print(f"      ✅ Éxito - Tiempo: {response_time:.0f}ms")
                    working_endpoints.append(
                        {
                            "url": url,
                            "response_time": response_time,
                            "status": "success",
                        }
                    )
                else:
                    print(f"      ❌ Sin respuesta válida")
                    failed_endpoints.append(
                        {"url": url, "error": "No valid response", "status": "failed"}
                    )

            except Exception as e:
                print(f"      ❌ Error: {type(e).__name__}: {str(e)}")
                failed_endpoints.append(
                    {"url": url, "error": str(e), "status": "error"}
                )

            # Restore original URL
            client.rpc_url = original_url

            # Small delay between tests
            time.sleep(0.5)

        # Summary
        print(f"\n📊 RESUMEN DE CONEXIONES:")
        print(f"   ✅ Endpoints funcionando: {len(working_endpoints)}")
        print(f"   ❌ Endpoints fallidos: {len(failed_endpoints)}")

        if working_endpoints:
            print(f"\n🏆 ENDPOINTS EXITOSOS:")
            for endpoint in working_endpoints:
                print(f"   • {endpoint['url']}")
                print(f"     Tiempo de respuesta: {endpoint['response_time']:.0f}ms")

        if failed_endpoints:
            print(f"\n⚠️  ENDPOINTS FALLIDOS:")
            for endpoint in failed_endpoints:
                print(f"   • {endpoint['url']}")
                print(f"     Error: {endpoint['error']}")

        # Test additional functionality if we have working endpoints
        if working_endpoints:
            print(f"\n🧪 Probando funcionalidades adicionales...")

            # Reset to best endpoint (fastest response)
            best_endpoint = min(working_endpoints, key=lambda x: x["response_time"])
            client.rpc_url = best_endpoint["url"]
            print(f"   Usando endpoint más rápido: {client.rpc_url}")

            # Test authentication
            print(f"\n   🔐 Probando autenticación...")
            try:
                if client.test_authentication():
                    print(f"      ✅ Autenticación exitosa")
                else:
                    print(f"      ❌ Fallo en autenticación")
            except Exception as e:
                print(f"      ❌ Error en autenticación: {e}")

            # Test balance query (if wallet address is provided)
            if os.getenv("FILECOIN_WALLET_ADDRESS"):
                print(f"\n   💰 Probando consulta de balance...")
                try:
                    balance_info = client.get_balance()
                    if balance_info.get("success"):
                        balances = balance_info.get("balances", {})
                        print(f"      ✅ Balance: {balances.get('FIL', '0')} FIL")
                    else:
                        print(f"      ❌ No se pudo obtener balance")
                except Exception as e:
                    print(f"      ❌ Error consultando balance: {e}")
            else:
                print(
                    f"   ⏭️  Omitiendo prueba de balance (no hay FILECOIN_WALLET_ADDRESS)"
                )

            # Test storage info
            print(f"\n   📦 Probando información de almacenamiento...")
            try:
                storage_info = client.get_storage_info()
                if storage_info.get("success"):
                    info = storage_info.get("info", {})
                    print(f"      ✅ Red: {info.get('network', 'Desconocida')}")
                    print(f"      ✅ Proveedores: {info.get('totalProviders', 'N/A')}")
                else:
                    print(f"      ❌ No se pudo obtener información de almacenamiento")
            except Exception as e:
                print(f"      ❌ Error obteniendo info de almacenamiento: {e}")

        # Final recommendation
        print(f"\n💡 RECOMENDACIONES:")
        if working_endpoints:
            fastest = min(working_endpoints, key=lambda x: x["response_time"])
            print(f"   • Usar endpoint más rápido: {fastest['url']}")
            print(
                f"   • Tiempo de respuesta promedio: {fastest['response_time']:.0f}ms"
            )
            print(f"   ✅ La aplicación debería funcionar correctamente")
        else:
            print(f"   ❌ Sin endpoints funcionales disponibles")
            print(f"   🔧 Verificar conexión a internet")
            print(f"   🔧 Revisar configuración de firewall")
            print(f"   🔧 Intentar más tarde (posibles problemas de red)")

        return len(working_endpoints) > 0

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {type(e).__name__}: {e}")
        return False


def main():
    """Main function"""
    print(f"Iniciando pruebas - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    success = test_filecoin_connection()

    print(f"\n" + "=" * 60)
    if success:
        print(f"🎉 PRUEBA COMPLETADA - AL MENOS UN ENDPOINT FUNCIONAL")
        exit_code = 0
    else:
        print(f"💥 PRUEBA FALLIDA - SIN ENDPOINTS FUNCIONALES")
        exit_code = 1

    print(f"Finalizado - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=" * 60)

    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
