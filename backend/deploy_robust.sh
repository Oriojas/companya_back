#!/bin/bash

# Script de Despliegue Robusto para Backend NFT Servicios
# Este script configura un entorno virtual Python y despliega el backend con manejo mejorado de errores

set -e  # Exit on any error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función para verificar comandos
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 no está instalado"
        return 1
    fi
    return 0
}

# Función para verificar archivos
check_file() {
    if [ ! -f "$1" ]; then
        log_error "No se encontró $1"
        return 1
    fi
    return 0
}

# Función para verificar dependencias Python
verify_python_deps() {
    log_info "Verificando dependencias Python..."

    # Lista de módulos a verificar
    local modules=("fastapi" "web3" "uvicorn" "pydantic" "dotenv" "eth_account")

    for module in "${modules[@]}"; do
        if python -c "import $module" 2>/dev/null; then
            log_success "$module cargado correctamente"
        else
            log_error "No se pudo cargar $module"
            return 1
        fi
    done

    return 0
}

# Función para limpiar en caso de error
cleanup() {
    log_warning "Limpiando en caso de error..."
    if [ -d "venv" ]; then
        log_info "Eliminando entorno virtual..."
        rm -rf venv
    fi
}

# Configurar trap para limpieza
trap cleanup ERR

echo -e "${BLUE}🚀 Iniciando despliegue robusto del Backend NFT Servicios${NC}"
echo "================================================================"

# Verificar que estamos en el directorio correcto
if ! check_file "requirements.txt"; then
    log_error "Ejecuta este script desde la carpeta backend del proyecto"
    exit 1
fi

# Verificar Python
if ! check_command "python3"; then
    log_error "Python3 no está instalado"
    echo "Instala con: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Verificar pip
if ! check_command "pip3"; then
    log_warning "pip3 no encontrado, intentando instalar..."
    sudo apt update && sudo apt install -y python3-pip
fi

# Crear entorno virtual
log_info "Creando entorno virtual Python..."
if [ -d "venv" ]; then
    log_warning "El entorno virtual ya existe. ¿Deseas recrearlo? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "Eliminando entorno virtual existente..."
        rm -rf venv
        python3 -m venv venv
    else
        log_info "Usando entorno virtual existente"
    fi
else
    python3 -m venv venv
fi

# Activar entorno virtual
log_info "Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
log_info "Actualizando pip..."
pip install --upgrade pip

# Instalar setuptools primero (evita problemas con web3)
log_info "Instalando setuptools y wheel..."
pip install setuptools wheel

# Instalar dependencias
log_info "Instalando dependencias desde requirements.txt..."
if check_file "requirements.txt"; then
    pip install -r requirements.txt
else
    log_error "No se pudo encontrar requirements.txt"
    exit 1
fi

# Verificar instalación de manera robusta
log_info "Verificando instalación de manera robusta..."
if verify_python_deps; then
    log_success "Todas las dependencias Python verificadas correctamente"
else
    log_error "Falló la verificación de dependencias"
    log_info "Intentando reinstalación..."
    pip install --force-reinstall -r requirements.txt
    if verify_python_deps; then
        log_success "Dependencias reinstaladas y verificadas correctamente"
    else
        log_error "No se pudieron resolver los problemas de dependencias"
        exit 1
    fi
fi

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    log_warning "Creando archivo .env desde .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_success "Archivo .env creado. Edita con tus configuraciones:"
        echo ""
        echo "   PRIVATE_KEY=tu_clave_privada"
        echo "   RPC_URL=https://sepolia-rollup.arbitrum.io/rpc"
        echo "   CONTRACT_ADDRESS=0xFF2E077849546cCB392f9e38B716A40fDC451798"
        echo "   CHAIN_ID=421614"
        echo ""
    else
        log_error "No se encontró .env.example"
        log_info "Crea manualmente el archivo .env con las siguientes variables:"
        cat << EOF

# Configuración Backend NFT Servicios
PRIVATE_KEY=tu_clave_privada_aqui
RPC_URL=https://sepolia-rollup.arbitrum.io/rpc
CONTRACT_ADDRESS=0xFF2E077849546cCB392f9e38B716A40fDC451798
CHAIN_ID=421614

EOF
    fi
else
    log_success "Archivo .env ya existe"
fi

# Verificar que el ABI del contrato está disponible
log_info "Verificando disponibilidad del ABI del contrato..."
if [ -f "../artifacts/contracts/ColeccionServiciosNFT.sol/ColeccionServiciosNFT.json" ]; then
    log_success "ABI del contrato encontrado"
else
    log_warning "ABI del contrato no encontrado en la ubicación esperada"
    log_info "Asegúrate de que el contrato esté compilado en la carpeta raíz del proyecto"
    log_info "Ejecuta en la carpeta raíz: npm run compile"
fi

# Mostrar información del sistema
echo ""
log_info "📊 Información del Sistema:"
echo "==========================="
python --version
pip --version
echo "Entorno virtual: $(which python)"
echo "Directorio actual: $(pwd)"

# Probar conexión básica
log_info "Probando conexión básica..."
if python -c "
import os
from dotenv import load_dotenv
load_dotenv()
if os.getenv('RPC_URL'):
    print('✅ Variables de entorno cargadas')
else:
    print('⚠️  RPC_URL no configurado')
" 2>/dev/null; then
    log_success "Configuración básica verificada"
else
    log_warning "Problemas con la configuración básica"
fi

# Instrucciones para ejecutar
echo ""
log_success "🎯 Instrucciones para ejecutar el servidor:"
echo "================================================"
echo "1. Configura las variables en .env (si no lo has hecho):"
echo "   - PRIVATE_KEY (tu clave privada del wallet)"
echo "   - RPC_URL (https://sepolia-rollup.arbitrum.io/rpc)"
echo "   - CONTRACT_ADDRESS (0xFF2E077849546cCB392f9e38B716A40fDC451798)"
echo "   - CHAIN_ID (421614)"
echo ""
echo "2. Activa el entorno virtual:"
echo "   source venv/bin/activate"
echo ""
echo "3. Ejecuta el servidor:"
echo "   python main.py"
echo ""
echo "4. El servidor estará disponible en:"
echo "   - API: http://localhost:8000"
echo "   - Documentación Swagger: http://localhost:8000/docs"
echo "   - Documentación ReDoc: http://localhost:8000/redoc"
echo "   - Health check: http://localhost:8000/health"
echo ""
echo "5. Para ejecutar en segundo plano:"
echo "   nohup python main.py > server.log 2>&1 &"
echo "   tail -f server.log  # para ver logs"

# Script de pruebas
echo ""
log_info "🧪 Para ejecutar pruebas automatizadas:"
echo "========================================"
echo "cd tests && python3 test_backend_completo.py"

echo ""
log_success "✅ Despliegue robusto completado exitosamente!"
log_success "El backend está listo para ejecutarse. Sigue las instrucciones arriba."

# Limpiar trap
trap - ERR
