#!/usr/bin/env python3
"""
Simple Log Viewer for NFT Servicios Backend
Muestra las transacciones registradas en transfer_log.json de forma amigable
"""

import json
from datetime import datetime
from pathlib import Path


def view_logs():
    """Muestra todas las transacciones del log"""
    log_file = Path(__file__).parent / "transfer_log.json"

    if not log_file.exists():
        print("❌ No se encontró el archivo transfer_log.json")
        print("💡 Asegúrate de que el backend haya ejecutado al menos una transacción")
        return

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo el archivo de log: {e}")
        return

    metadata = data.get("metadata", {})
    transactions = data.get("transactions", [])

    print("📊 REGISTRO DE TRANSACCIONES NFT SERVICIOS")
    print("=" * 60)
    print(f"📅 Creado: {metadata.get('created_at', 'N/A')}")
    print(f"🌐 Red: {metadata.get('network', 'N/A')}")
    print(f"📄 Contrato: {metadata.get('contract_address', 'N/A')}")
    print(f"🔄 Total transacciones: {metadata.get('total_transactions', 0)}")
    print(f"📝 Última actualización: {metadata.get('last_updated', 'N/A')}")
    print("=" * 60)

    if not transactions:
        print("\n📭 No hay transacciones registradas aún")
        return

    print(f"\n🔄 ÚLTIMAS {len(transactions)} TRANSACCIONES:")
    print("-" * 60)

    for i, tx in enumerate(transactions, 1):
        print(f"\n#{i}")
        print(f"  ⏰ Fecha: {tx.get('timestamp', 'N/A')}")
        print(f"  🔗 Hash: {tx.get('transaction_hash', 'N/A')}")
        print(f"  📄 Función: {tx.get('function', 'N/A')}")
        print(f"  ✅ Estado: {tx.get('status', 'N/A')}")
        print(f"  📦 Bloque: {tx.get('block_number', 'N/A')}")
        print(f"  ⛽ Gas usado: {tx.get('gas_used', 'N/A')}")

        # Mostrar parámetros
        params = tx.get("parameters", {})
        if params:
            print(f"  📋 Parámetros:")
            for key, value in params.items():
                print(f"     • {key}: {value}")

        # Mostrar resultados
        result = tx.get("result", {})
        if result:
            print(f"  📊 Resultados:")
            for key, value in result.items():
                if key not in ["transactionHash", "blockNumber", "gasUsed", "status"]:
                    print(f"     • {key}: {value}")

        # URL de Arbiscan
        arbiscan_url = tx.get("arbiscan_url", "")
        if arbiscan_url:
            print(f"  🔍 Arbiscan: {arbiscan_url}")

        print("-" * 40)


def show_statistics():
    """Muestra estadísticas del log"""
    log_file = Path(__file__).parent / "transfer_log.json"

    if not log_file.exists():
        print("❌ No se encontró el archivo transfer_log.json")
        return

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo el archivo de log: {e}")
        return

    transactions = data.get("transactions", [])

    if not transactions:
        print("📭 No hay transacciones para mostrar estadísticas")
        return

    # Calcular estadísticas
    function_counts = {}
    status_counts = {}
    total_gas = 0
    token_ids = set()

    for tx in transactions:
        function = tx.get("function", "unknown")
        status = tx.get("status", "unknown")
        gas_used = tx.get("gas_used", 0)

        function_counts[function] = function_counts.get(function, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
        total_gas += int(gas_used) if gas_used else 0

        # Extraer token_id de parámetros
        params = tx.get("parameters", {})
        token_id = params.get("tokenId")
        if token_id is not None:
            token_ids.add(token_id)

    print("\n📊 ESTADÍSTICAS DEL LOG")
    print("=" * 40)
    print(f"📈 Total transacciones: {len(transactions)}")
    print(f"⛽ Total gas usado: {total_gas:,}")
    print(f"🎫 Tokens involucrados: {len(token_ids)}")

    print(f"\n📋 Por función:")
    for func, count in function_counts.items():
        print(f"   • {func}: {count}")

    print(f"\n✅ Por estado:")
    for status, count in status_counts.items():
        print(f"   • {status}: {count}")


def search_transaction(tx_hash: str):
    """Busca una transacción específica por hash"""
    log_file = Path(__file__).parent / "transfer_log.json"

    if not log_file.exists():
        print("❌ No se encontró el archivo transfer_log.json")
        return

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo el archivo de log: {e}")
        return

    transactions = data.get("transactions", [])

    for tx in transactions:
        if tx.get("transaction_hash") == tx_hash:
            print(f"\n🎯 TRANSACCIÓN ENCONTRADA")
            print("=" * 50)
            print(f"🔗 Hash: {tx.get('transaction_hash')}")
            print(f"📄 Función: {tx.get('function')}")
            print(f"⏰ Fecha: {tx.get('timestamp')}")
            print(f"✅ Estado: {tx.get('status')}")
            print(f"📦 Bloque: {tx.get('block_number')}")
            print(f"⛽ Gas usado: {tx.get('gas_used')}")

            arbiscan_url = tx.get("arbiscan_url", "")
            if arbiscan_url:
                print(f"\n🔍 Ver en Arbiscan:")
                print(f"   {arbiscan_url}")
            return

    print(f"❌ No se encontró la transacción con hash: {tx_hash}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            show_statistics()
        elif sys.argv[1] == "search" and len(sys.argv) > 2:
            search_transaction(sys.argv[2])
        else:
            print("Uso:")
            print("  python3 view_logs.py           # Ver todas las transacciones")
            print("  python3 view_logs.py stats     # Ver estadísticas")
            print("  python3 view_logs.py search <hash>  # Buscar transacción")
    else:
        view_logs()
        show_statistics()
