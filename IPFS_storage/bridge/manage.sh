#!/bin/bash

# Filecoin Bridge Service Management Script
# Usage: ./manage.sh [start|stop|restart|status|logs]

PORT=${PORT:-3001}
SERVICE_NAME="filecoin-bridge-service"
PID_FILE="/tmp/${SERVICE_NAME}.pid"
LOG_FILE="/tmp/${SERVICE_NAME}.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if service is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Get processes using the port
get_port_processes() {
    lsof -ti :$PORT 2>/dev/null
}

# Kill processes using the port
kill_port_processes() {
    local pids=$(get_port_processes)
    if [ -n "$pids" ]; then
        print_warning "Killing processes using port $PORT: $pids"
        echo $pids | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Start the service
start_service() {
    if is_running; then
        print_warning "Service is already running (PID: $(cat $PID_FILE))"
        return 0
    fi

    # Kill any processes using the port
    kill_port_processes

    print_status "Starting $SERVICE_NAME..."

    # Start the service in background
    nohup npm start > "$LOG_FILE" 2>&1 &
    local pid=$!

    # Save PID
    echo $pid > "$PID_FILE"

    # Wait a moment and check if it's still running
    sleep 3
    if kill -0 "$pid" 2>/dev/null; then
        print_success "Service started successfully (PID: $pid)"
        print_status "Logs: $LOG_FILE"

        # Show first few lines of logs
        sleep 2
        tail -20 "$LOG_FILE"
    else
        print_error "Failed to start service"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop the service
stop_service() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_status "Stopping $SERVICE_NAME (PID: $pid)..."

        kill "$pid"

        # Wait for graceful shutdown
        local count=0
        while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done

        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            print_warning "Forcing kill of service..."
            kill -9 "$pid" 2>/dev/null || true
        fi

        rm -f "$PID_FILE"
        print_success "Service stopped"
    else
        print_warning "Service is not running"
    fi

    # Also kill any processes still using the port
    kill_port_processes
}

# Show service status
show_status() {
    echo "=== $SERVICE_NAME Status ==="

    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_success "Service is running (PID: $pid)"

        # Show process info
        echo
        print_status "Process information:"
        ps -p "$pid" -o pid,ppid,cmd,etime 2>/dev/null || print_warning "Process details not available"

        # Show port usage
        echo
        print_status "Port usage:"
        lsof -i :$PORT 2>/dev/null || print_warning "No processes found on port $PORT"

    else
        print_warning "Service is not running"

        # Check if port is being used by other processes
        local port_pids=$(get_port_processes)
        if [ -n "$port_pids" ]; then
            print_warning "Port $PORT is being used by other processes: $port_pids"
            echo
            print_status "Processes on port $PORT:"
            lsof -i :$PORT 2>/dev/null
        fi
    fi

    echo
    print_status "Log file: $LOG_FILE"
    if [ -f "$LOG_FILE" ]; then
        echo "Last 10 lines of log:"
        tail -10 "$LOG_FILE"
    else
        print_warning "No log file found"
    fi
}

# Show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "Showing logs from $LOG_FILE"
        echo "===================="

        if [ "$2" = "-f" ]; then
            tail -f "$LOG_FILE"
        else
            tail -50 "$LOG_FILE"
            echo
            print_status "Use '$0 logs -f' to follow logs in real-time"
        fi
    else
        print_error "Log file not found: $LOG_FILE"
    fi
}

# Restart service
restart_service() {
    print_status "Restarting $SERVICE_NAME..."
    stop_service
    sleep 2
    start_service
}

# Clean up old files
cleanup() {
    print_status "Cleaning up..."

    # Remove PID file if process is not running
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ! kill -0 "$pid" 2>/dev/null; then
            rm -f "$PID_FILE"
            print_status "Removed stale PID file"
        fi
    fi

    # Clean old log files (keep last 5)
    if [ -f "$LOG_FILE" ]; then
        # Rotate log if it's too large (>10MB)
        if [ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt 10485760 ]; then
            mv "$LOG_FILE" "${LOG_FILE}.old"
            print_status "Rotated large log file"
        fi
    fi
}

# Show help
show_help() {
    echo "Filecoin Bridge Service Management Script"
    echo
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  start      Start the service"
    echo "  stop       Stop the service"
    echo "  restart    Restart the service"
    echo "  status     Show service status"
    echo "  logs [-f]  Show logs (-f to follow)"
    echo "  cleanup    Clean up old files"
    echo "  kill-port  Kill all processes using port $PORT"
    echo
    echo "Environment Variables:"
    echo "  PORT       Port to use (default: 3001)"
    echo
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 logs -f"
    echo "  PORT=3002 $0 start"
}

# Main script logic
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$@"
        ;;
    cleanup)
        cleanup
        ;;
    kill-port)
        kill_port_processes
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac
