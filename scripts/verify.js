const { ethers, network, run } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("======================================================================");
  console.log("🔍 VERIFICACIÓN DE CONTRATO EN ARBISCAN");
  console.log("======================================================================\n");

  // Verificar que la API key esté configurada
  if (!process.env.ARBISCAN_API_KEY) {
    console.log("⚠️  ARBISCAN_API_KEY no configurada en .env");
    console.log("ℹ️  Puedes obtener una API key en: https://arbiscan.io/apis");
    console.log("ℹ️  La verificación es opcional, el contrato funciona sin ella");
    return;
  }

  console.log("📋 Información de la red:");
  console.log(`   Red: ${network.name}`);
  console.log(`   Chain ID: ${network.config.chainId}`);

  // Cargar información del último despliegue
  const deploymentsDir = path.join(__dirname, "..", "deployments");
  const latestDeploymentFile = path.join(deploymentsDir, "latest-deployment.json");

  if (!fs.existsSync(latestDeploymentFile)) {
    console.log("❌ No se encontró información de despliegue. Ejecuta 'npm run deploy' primero.");
    process.exit(1);
  }

  const deploymentInfo = JSON.parse(fs.readFileSync(latestDeploymentFile, 'utf8'));
  const contractAddress = deploymentInfo.contractAddress;

  console.log("\n📋 Información del contrato:");
  console.log(`   Dirección: ${contractAddress}`);
  console.log(`   Nombre: ${deploymentInfo.contractName}`);
  console.log(`   Símbolo: ${deploymentInfo.contractSymbol}`);
  console.log(`   Fecha de despliegue: ${deploymentInfo.deploymentDate}`);

  // Verificar el contrato en Arbiscan
  console.log("\n🔍 Verificando contrato en Arbiscan...");

  try {
    await run("verify:verify", {
      address: contractAddress,
      constructorArguments: [],
    });
    console.log("✅ Contrato verificado exitosamente en Arbiscan");

    // Actualizar información del despliegue
    deploymentInfo.verified = true;
    deploymentInfo.verificationDate = new Date().toISOString();
    fs.writeFileSync(latestDeploymentFile, JSON.stringify(deploymentInfo, null, 2));

    console.log("\n💾 Información actualizada en archivo de despliegue");

  } catch (error) {
    if (error.message.includes("Already Verified")) {
      console.log("ℹ️  El contrato ya estaba verificado anteriormente");
    } else {
      console.log("❌ Error en verificación:", error.message);
      console.log("\nℹ️  Puedes verificar manualmente en:");
      console.log(`   https://sepolia.arbiscan.io/verifyContract`);
      console.log("   Con los siguientes parámetros:");
      console.log(`   - Dirección del contrato: ${contractAddress}`);
      console.log(`   - Nombre del contrato: ${deploymentInfo.contractName}`);
      console.log(`   - Versión del compilador: v0.8.19`);
      console.log(`   - Optimización: Sí (200 runs)`);
      console.log(`   - Constructor arguments: (vacío)`);
    }
  }

  // Mostrar enlaces útiles
  console.log("\n🔗 Enlaces útiles:");
  console.log(`   📊 Arbiscan: https://sepolia.arbiscan.io/address/${contractAddress}`);
  console.log(`   📝 Transacción: https://sepolia.arbiscan.io/tx/${deploymentInfo.transactionHash}`);
  console.log(`   🖼️  OpenSea Testnet: https://testnets.opensea.io/assets/arbitrum-sepolia/${contractAddress}`);

  console.log("\n======================================================================");
  console.log("✅ VERIFICACIÓN COMPLETADA");
  console.log("======================================================================");
  console.log(`📍 Dirección del contrato: ${contractAddress}`);
  console.log(`🔗 Arbiscan: https://sepolia.arbiscan.io/address/${contractAddress}`);
  console.log("======================================================================\n");
}

// Manejo de errores
main().catch((error) => {
  console.error("\n❌ Error durante la verificación:");
  console.error(error);
  process.exitCode = 1;
});

module.exports = main;
