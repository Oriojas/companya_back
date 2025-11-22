import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class TransactionLogger:
    """Sistema de registro de transacciones para el backend NFT"""

    def __init__(self, log_file: str = "transfer_log.json"):
        self.log_file = Path(__file__).parent / log_file
        self.arbiscan_base_url = "https://sepolia.arbiscan.io/tx"
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Asegura que el archivo de log exista con estructura correcta"""
        if not self.log_file.exists():
            initial_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "description": "Registro de transacciones NFT Servicios",
                    "network": "Arbitrum Sepolia",
                    "contract_address": "0xFF2E077849546cCB392f9e38B716A40fDC451798",
                    "version": "1.0.0",
                },
                "transactions": [],
            }
            self._write_log(initial_data)

    def _write_log(self, data: Dict[str, Any]):
        """Escribe datos en el archivo de log"""
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error escribiendo log: {e}")

    def _read_log(self) -> Dict[str, Any]:
        """Lee el archivo de log"""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error leyendo log: {e}")
            return {"metadata": {}, "transactions": []}

    def log_transaction(
        self,
        tx_hash: str,
        function_name: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        status: str = "success",
    ) -> None:
        """Registra una transacción en el log"""

        # Construir URL de Arbiscan
        arbiscan_url = f"{self.arbiscan_base_url}/{tx_hash}"

        # Crear entrada de transacción
        transaction_entry = {
            "timestamp": datetime.now().isoformat(),
            "transaction_hash": tx_hash,
            "arbiscan_url": arbiscan_url,
            "function": function_name,
            "parameters": parameters,
            "result": result,
            "status": status,
            "block_number": result.get("blockNumber"),
            "gas_used": result.get("gasUsed"),
            "network": "arbitrumSepolia",
        }

        # Leer log existente
        log_data = self._read_log()

        # Agregar nueva transacción al inicio (más reciente primero)
        log_data["transactions"].insert(0, transaction_entry)

        # Limitar a las últimas 1000 transacciones
        if len(log_data["transactions"]) > 1000:
            log_data["transactions"] = log_data["transactions"][:1000]

        # Actualizar metadata
        log_data["metadata"]["last_updated"] = datetime.now().isoformat()
        log_data["metadata"]["total_transactions"] = len(log_data["transactions"])

        # Escribir log actualizado
        self._write_log(log_data)

        print(f"📝 Transacción registrada: {tx_hash}")
        print(f"🔗 Arbiscan: {arbiscan_url}")

    def get_transaction_history(self, limit: Optional[int] = None) -> list:
        """Obtiene el historial de transacciones"""
        log_data = self._read_log()
        transactions = log_data.get("transactions", [])

        if limit:
            return transactions[:limit]
        return transactions

    def get_transaction_by_hash(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Busca una transacción por su hash"""
        transactions = self.get_transaction_history()
        for tx in transactions:
            if tx.get("transaction_hash") == tx_hash:
                return tx
        return None

    def get_transactions_by_function(self, function_name: str) -> list:
        """Obtiene transacciones por nombre de función"""
        transactions = self.get_transaction_history()
        return [tx for tx in transactions if tx.get("function") == function_name]

    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del log"""
        transactions = self.get_transaction_history()

        if not transactions:
            return {}

        # Contar por función
        function_counts = {}
        status_counts = {}
        total_gas_used = 0

        for tx in transactions:
            func = tx.get("function", "unknown")
            status = tx.get("status", "unknown")
            gas_used = tx.get("gas_used", 0)

            function_counts[func] = function_counts.get(func, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
            total_gas_used += int(gas_used) if gas_used else 0

        return {
            "total_transactions": len(transactions),
            "function_counts": function_counts,
            "status_counts": status_counts,
            "total_gas_used": total_gas_used,
            "first_transaction": transactions[-1].get("timestamp")
            if transactions
            else None,
            "last_transaction": transactions[0].get("timestamp")
            if transactions
            else None,
        }

    def clear_log(self):
        """Limpia el log (mantiene metadata)"""
        log_data = self._read_log()
        log_data["transactions"] = []
        log_data["metadata"]["last_cleared"] = datetime.now().isoformat()
        self._write_log(log_data)
        print("🗑️ Log limpiado")


# Instancia global para uso fácil
transaction_logger = TransactionLogger()


# Funciones de conveniencia
def log_transaction(
    tx_hash: str,
    function_name: str,
    parameters: Dict[str, Any],
    result: Dict[str, Any],
    status: str = "success",
):
    """Función de conveniencia para registrar transacciones"""
    return transaction_logger.log_transaction(
        tx_hash, function_name, parameters, result, status
    )


def get_transaction_history(limit: Optional[int] = None):
    """Función de conveniencia para obtener historial"""
    return transaction_logger.get_transaction_history(limit)


def get_statistics():
    """Función de conveniencia para obtener estadísticas"""
    return transaction_logger.get_statistics()
