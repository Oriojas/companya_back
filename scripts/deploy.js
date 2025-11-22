const { ethers, network } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("======================================================================");
  console.log("🚀 DESPLIEGUE DE CONTRATO NFT EN ARBITRUM SEPOLIA");
  console.log("======================================================================\n");

  // Verificar que las variables de entorno estén configuradas
  if (!process.env.PRIVATE_KEY) {
    throw new Error("❌ PRIVATE_KEY no configurada en .env");
  }

  if (!process.env.ARBITRUM_SEPOLIA_RPC_URL) {
    throw new Error("❌ ARBITRUM_SEPOLIA_RPC_URL no configurada en .env");
  }

  console.log("📋 Información de la red:");
  console.log(`   Red: ${network.name}`);
  console.log(`   Chain ID: ${network.config.chainId}`);
  console.log(`   URL RPC: ${process.env.ARBITRUM_SEPOLIA_RPC_URL}`);

  // Obtener el deployer
  const [deployer] = await ethers.getSigners();
  console.log("\n👤 Información del deployer:");
  console.log(`   Dirección: ${deployer.address}`);
  console.log(`   Balance: ${ethers.formatEther(await deployer.provider.getBalance(deployer.address))} ETH`);

  // Verificar balance suficiente
  const balance = await deployer.provider.getBalance(deployer.address);
  if (ethers.formatEther(balance) < 0.001) {
    throw new Error(`❌ Balance insuficiente. Necesitas al menos 0.001 ETH. Balance actual: ${ethers.formatEther(balance)} ETH`);
  }

  console.log("\n🔨 Compilando contrato...");
  await run("compile");
  console.log("✅ Contrato compilado exitosamente");

  // Desplegar el contrato
  console.log("\n🚀 Desplegando contrato ColeccionServiciosNFT...");

  const ContractFactory = await ethers.getContractFactory("ColeccionServiciosNFT");
  const contract = await ContractFactory.deploy();

  await contract.waitForDeployment();
  const contractAddress = await contract.getAddress();

  console.log("✅ Contrato desplegado exitosamente");
  console.log(`📍 Dirección del contrato: ${contractAddress}`);

  // Obtener información de la transacción
  const deploymentTransaction = contract.deploymentTransaction();
  const receipt = await deploymentTransaction.wait();

  console.log("\n📊 Información del despliegue:");
  console.log(`   Hash de transacción: ${receipt.hash}`);
  console.log(`   Bloque: ${receipt.blockNumber}`);
  console.log(`   Gas usado: ${receipt.gasUsed.toString()}`);
  console.log(`   Costo en ETH: ${ethers.formatEther(receipt.gasUsed * receipt.gasPrice)} ETH`);

  // Esperar algunos bloques para asegurar que la transacción esté confirmada
  console.log("\n⏳ Esperando confirmaciones...");
  await contract.deploymentTransaction().wait(5);
  console.log("✅ Transacción confirmada (5 bloques)");

  // Guardar información del despliegue
  const deploymentInfo = {
    contractName: "ColeccionServiciosNFT",
    contractAddress: contractAddress,
    network: network.name,
    chainId: network.config.chainId,
    deployer: deployer.address,
    transactionHash: receipt.hash,
    blockNumber: receipt.blockNumber,
    gasUsed: receipt.gasUsed.toString(),
    deploymentDate: new Date().toISOString(),
    contractSymbol: "CSNFT",
    contractVersion: "1.0.0"
  };

  // Crear directorio deployments si no existe
  const deploymentsDir = path.join(__dirname, "..", "deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  // Guardar archivo de despliegue
  const deploymentFile = path.join(deploymentsDir, `deployment-${network.name}-${Date.now()}.json`);
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

  // Actualizar último despliegue
  const latestDeploymentFile = path.join(deploymentsDir, "latest-deployment.json");
  fs.writeFileSync(latestDeploymentFile, JSON.stringify(deploymentInfo, null, 2));

  console.log("\n💾 Información del despliegue guardada:");
  console.log(`   Archivo específico: ${deploymentFile}`);
  console.log(`   Último despliegue: ${latestDeploymentFile}`);

  // Mostrar enlaces útiles
  console.log("\n🔗 Enlaces útiles:");
  console.log(`   📊 Arbiscan: https://sepolia.arbiscan.io/address/${contractAddress}`);
  console.log(`   📝 Transacción: https://sepolia.arbiscan.io/tx/${receipt.hash}`);
  console.log(`   🖼️  OpenSea Testnet: https://testnets.opensea.io/assets/arbitrum-sepolia/${contractAddress}`);

  console.log("\n======================================================================");
  console.log("✅ DESPLIEGUE COMPLETADO");
  console.log("======================================================================");
  console.log(`📍 Dirección del contrato: ${contractAddress}`);
  console.log(`🔗 Arbiscan: https://sepolia.arbiscan.io/address/${contractAddress}`);
  console.log("======================================================================");
  console.log("\n🎯 Próximo paso: Ejecuta 'npm run verify' para verificar el contrato en Arbiscan");
  console.log("======================================================================\n");

  return {
    contractAddress,
    transactionHash: receipt.hash,
    blockNumber: receipt.blockNumber,
    gasUsed: receipt.gasUsed.toString()
  };
}

// Manejo de errores
main().catch((error) => {
  console.error("\n❌ Error durante el despliegue:");
  console.error(error);
  process.exitCode = 1;
});

module.exports = main;
