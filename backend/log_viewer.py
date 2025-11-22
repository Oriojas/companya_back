#!/usr/bin/env python3
"""
Log Viewer para NFT Servicios Backend
Script para visualizar y analizar el registro de transacciones de manera amigable
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class LogViewer:
    def __init__(self, log_file: str = "transfer_log.json"):
        self.log_file = Path(__file__).parent / log_file
        self.arbiscan_base_url = "https://sepolia.arbiscan.io/tx"

    def load_logs(self) -> Dict[str, Any]:
        """Carga los logs desde el archivo"""
        if not self.log_file.exists():
            print(f"❌ Archivo de log no encontrado: {self.log_file}")
            return {}

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error cargando logs: {e}")
            return {}

    def display_summary(self):
        """Muestra un resumen general del log"""
        data = self.load_logs()
        if not data:
            return

        metadata = data.get("metadata", {})
        transactions = data.get("transactions", [])

        print("📊 RESUMEN DEL REGISTRO DE TRANSACCIONES")
        print("=" * 50)
        print(f"📅 Creado: {metadata.get('created_at', 'N/A')}")
        print(f"🔄 Última actualización: {metadata.get('last_updated', 'N/A')}")
        print(f"📈 Total de transacciones: {len(transactions)}")
        print(f"🌐 Red: {metadata.get('network', 'N/A')}")
        print(f"📄 Contrato: {metadata.get('contract_address', 'N/A')}")
        print()

    def display_transactions(self, limit: int = 10, show_details: bool = False):
        """Muestra las transacciones más recientes"""
        data = self.load_logs()
        if not data:
            return

        transactions = data.get("transactions", [])[:limit]

        if not transactions:
            print("📭 No hay transacciones registradas")
            return

        print(f"📋 ÚLTIMAS {len(transactions)} TRANSACCIONES")
        print("=" * 50)

        for i, tx in enumerate(transactions, 1):
            print(f"\n{i}. {tx.get('function', 'N/A')}")
            print(f"   🕐 {tx.get('timestamp', 'N/A')}")
            print(f"   🔗 Hash: {tx.get('transaction_hash', 'N/A')}")
            print(f"   📦 Bloque: {tx.get('block_number', 'N/A')}")
            print(f"   ⛽ Gas usado: {tx.get('gas_used', 'N/A')}")
            print(f"   ✅ Estado: {tx.get('status', 'N/A')}")
            print(f"   🔍 Arbiscan: {tx.get('arbiscan_url', 'N/A')}")

            if show_details:
                params = tx.get("parameters", {})
                if params:
                    print("   📝 Parámetros:")
                    for key, value in params.items():
                        print(f"      - {key}: {value}")

                result = tx.get("result", {})
                if result and len(result) > 1:  # Más que solo el hash
                    print("   📊 Resultado:")
                    for key, value in result.items():
                        if key not in [
                            "transactionHash",
                            "blockNumber",
                            "gasUsed",
                            "status",
                        ]:
                            print(f"      - {key}: {value}")

    def display_statistics(self):
        """Muestra estadísticas detalladas"""
        data = self.load_logs()
        if not data:
            return

        transactions = data.get("transactions", [])

        if not transactions:
            print("📭 No hay transacciones para analizar")
            return

        # Calcular estadísticas
        function_counts = {}
        status_counts = {}
        total_gas = 0
        tokens_involved = set()

        for tx in transactions:
            func = tx.get("function", "unknown")
            status = tx.get("status", "unknown")
            gas_used = tx.get("gas_used", 0)

            function_counts[func] = function_counts.get(func, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
            total_gas += int(gas_used) if gas_used else 0

            # Extraer token_id de parámetros o resultado
            params = tx.get("parameters", {})
            result = tx.get("result", {})
            token_id = (
                params.get("tokenId") or result.get("tokenId") or result.get("token_id")
            )
            if token_id is not None:
                tokens_involved.add(token_id)

        print("📈 ESTADÍSTICAS DETALLADAS")
        print("=" * 50)
        print(f"📊 Total de transacciones: {len(transactions)}")
        print(
            f"⛽ Gas total utilizado: {total_gas:,} wei ({total_gas / 1e6:.2f} millones)"
        )
        print(f"🎫 Tokens involucrados: {len(tokens_involved)}")
        if tokens_involved:
            print(f"   IDs: {sorted(list(tokens_involved))}")

        print("\n📋 Distribución por función:")
        for func, count in sorted(
            function_counts.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / len(transactions)) * 100
            print(f"   {func}: {count} ({percentage:.1f}%)")

        print("\n✅ Distribución por estado:")
        for status, count in status_counts.items():
            percentage = (count / len(transactions)) * 100
            print(f"   {status}: {count} ({percentage:.1f}%)")

    def search_transactions(self, search_term: str):
        """Busca transacciones por término"""
        data = self.load_logs()
        if not data:
            return

        transactions = data.get("transactions", [])
        search_term = search_term.lower()

        results = []
        for tx in transactions:
            # Buscar en función, hash, parámetros
            if (
                search_term in tx.get("function", "").lower()
                or search_term in tx.get("transaction_hash", "").lower()
                or any(
                    search_term in str(value).lower()
                    for value in tx.get("parameters", {}).values()
                )
            ):
                results.append(tx)

        print(f"🔍 RESULTADOS DE BÚSQUEDA: '{search_term}'")
        print("=" * 50)

        if not results:
            print("❌ No se encontraron transacciones")
            return

        for i, tx in enumerate(results, 1):
            print(f"\n{i}. {tx.get('function', 'N/A')}")
            print(f"   🕐 {tx.get('timestamp', 'N/A')}")
            print(f"   🔗 Hash: {tx.get('transaction_hash', 'N/A')}")
            print(f"   📦 Bloque: {tx.get('block_number', 'N/A')}")
            print(f"   🔍 Arbiscan: {tx.get('arbiscan_url', 'N/A')}")

    def export_to_csv(self, output_file: str = "transactions_export.csv"):
        """Exporta las transacciones a CSV"""
        data = self.load_logs()
        if not data:
            return

        transactions = data.get("transactions", [])

        if not transactions:
            print("📭 No hay transacciones para exportar")
            return

        csv_lines = [
            "timestamp,function,transaction_hash,block_number,gas_used,status,arbiscan_url,parameters"
        ]

        for tx in transactions:
            timestamp = tx.get("timestamp", "")
            function = tx.get("function", "")
            tx_hash = tx.get("transaction_hash", "")
            block = tx.get("block_number", "")
            gas = tx.get("gas_used", "")
            status = tx.get("status", "")
            arbiscan = tx.get("arbiscan_url", "")
            params = json.dumps(tx.get("parameters", {}), ensure_ascii=False)

            csv_line = f'"{timestamp}","{function}","{tx_hash}",{block},{gas},"{status}","{arbiscan}","{params}"'
            csv_lines.append(csv_line)

        output_path = Path(__file__).parent / output_file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(csv_lines))
            print(f"✅ Exportado a: {output_path}")
            print(f"📄 {len(transactions)} transacciones exportadas")
        except Exception as e:
            print(f"❌ Error exportando: {e}")


def main():
    """Función principal con interfaz de menú"""
    viewer = LogViewer()

    while True:
        print("\n" + "=" * 60)
        print("👁️  VISOR DE LOGS - NFT SERVICIOS BACKEND")
        print("=" * 60)
        print("1. 📊 Resumen general")
        print("2. 📋 Ver transacciones recientes")
        print("3. 🔍 Ver transacciones con detalles")
        print("4. 📈 Estadísticas detalladas")
        print("5. 🔎 Buscar transacciones")
        print("6. 💾 Exportar a CSV")
        print("7. 🚪 Salir")
        print("-" * 60)

        choice = input("Selecciona una opción (1-7): ").strip()

        if choice == "1":
            viewer.display_summary()
        elif choice == "2":
            try:
                limit = int(
                    input("Número de transacciones a mostrar (default 10): ") or "10"
                )
            except ValueError:
                limit = 10
            viewer.display_transactions(limit=limit)
        elif choice == "3":
            try:
                limit = int(
                    input("Número de transacciones a mostrar (default 10): ") or "10"
                )
            except ValueError:
                limit = 10
            viewer.display_transactions(limit=limit, show_details=True)
        elif choice == "4":
            viewer.display_statistics()
        elif choice == "5":
            search_term = input("Término de búsqueda: ").strip()
            if search_term:
                viewer.search_transactions(search_term)
            else:
                print("❌ Ingresa un término de búsqueda")
        elif choice == "6":
            output_file = input(
                "Nombre del archivo CSV (default: transactions_export.csv): "
            ).strip()
            if not output_file:
                output_file = "transactions_export.csv"
            viewer.export_to_csv(output_file)
        elif choice == "7":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")

        input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    main()
