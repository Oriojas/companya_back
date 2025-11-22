# ⚡ Quick Start - Despliegue Simplificado

## 📋 Resumen
Framework **Hardhat** configurado para desplegar el contrato NFT `ColeccionServiciosNFT` en Arbitrum Sepolia con solo 3 comandos.

**Comandos principales:**
- `npm run compile` - Compilar contrato
- `npm run deploy` - Desplegar en Arbitrum Sepolia  
- `npm run verify` - Verificar en Arbiscan

---

## 🚀 Instalación

```bash
npm install
```

Instala todas las dependencias necesarias para el despliegue.

---

## ⚙️ Configurar Variables de Entorno

```bash
cp .env.example .env
```

Edita `.env` con:

```env
# Network Configuration
ARBITRUM_SEPOLIA_RPC_URL=https://sepolia-rollup.arbitrum.io/rpc

# Private Key (SIN el prefijo 0x)
PRIVATE_KEY=tu_clave_privada_sin_0x

# Verification API Keys (opcional)
ARBISCAN_API_KEY=tu_arbiscan_api_key_here
```

### ⚠️ Obtener ETH de Prueba

Necesitas **> 0.001 ETH** en Arbitrum Sepolia:
- Faucet: https://faucet.quicknode.com/arbitrum/sepolia

---

## 🔨 Compilar

```bash
npm run compile
```

Compila el contrato antes del despliegue.

---

## 🌐 DESPLEGAR

```bash
npm run deploy
```

**Este comando:**
1. ✅ Compila el contrato
2. ✅ Despliega en Arbitrum Sepolia
3. ✅ Guarda información del despliegue

**¡LISTO! Tu contrato está en Arbitrum Sepolia**

---

## 📁 Archivos Generados

Después del despliegue se crea:
```
deployments/
├── latest-deployment.json                # Info del último despliegue
└── deployment-arbitrumSepolia-*.json    # Histórico de despliegues
```

La carpeta `deployments` NO está ignorada para uso posterior.

---

## 🔍 VERIFICAR (Opcional)

```bash
npm run verify
```

Verifica el contrato en Arbiscan (requiere `ARBISCAN_API_KEY`).

---

## 📋 Checklist Rápido

- [ ] `npm install` completado
- [ ] `.env` configurado con PRIVATE_KEY
- [ ] ETH de prueba en wallet (> 0.001)
- [ ] `npm run compile` exitoso
- [ ] `npm run deploy` exitoso
- [ ] Contrato visible en Arbiscan
- [ ] Dirección guardada en lugar seguro

---

## 🔗 Links Útiles

| Recurso | URL |
|---------|-----|
| Arbiscan Sepolia | https://sepolia.arbiscan.io/ |
| Faucet ETH | https://faucet.quicknode.com/arbitrum/sepolia |
| OpenSea Testnet | https://testnets.opensea.io/ |
| Hardhat Docs | https://hardhat.org/ |

---

## 🆘 Problemas Comunes

**Error: "Invalid private key"**
- Asegúrate que `PRIVATE_KEY` NO tenga `0x`
- Debe tener 64 caracteres hexadecimales

**Error: "Insufficient balance"**
- Necesitas > 0.001 ETH en testnet
- Faucet: https://faucet.quicknode.com/arbitrum/sepolia

---

## ⚠️ Seguridad

- **NUNCA** hagas commit de `.env`
- **NUNCA** compartas tu `PRIVATE_KEY`
- Usa wallets separadas para testnet y mainnet

---

## 📚 Documentación

- **README Completo**: Ver `README.md`

---

## 🎉 ¡Listo!

Una vez ejecutes `npm run deploy` exitosamente:

1. ✅ Tu contrato está en Arbitrum Sepolia
2. ✅ Información guardada en `deployments/`
3. ✅ Puedes interactuar con él desde Arbiscan

**Próximos pasos:**
- Verificar contrato: `npm run verify`
- Integrar en frontend usando ABI de `artifacts/`

---

**Comandos**: `compile` | `deploy` | `verify`