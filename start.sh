#!/bin/bash

# Function to check OS type and install tmux if needed
check_and_install_tmux() {
    if ! command -v tmux &> /dev/null; then
        echo "tmux not found. Installing..."

        # Detect operating system
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux distributions
            if command -v apt-get &> /dev/null; then
                echo "Detected apt package manager"

                # Check if apt is locked and wait if needed
                apt_locked=true
                max_attempts=5
                attempt=1

                while $apt_locked && [ $attempt -le $max_attempts ]; do
                    echo "Attempt $attempt of $max_attempts to acquire apt lock..."

                    # Check if apt is locked
                    if sudo lsof /var/lib/apt/lists/lock > /dev/null 2>&1 || sudo lsof /var/lib/dpkg/lock > /dev/null 2>&1 || sudo lsof /var/lib/dpkg/lock-frontend > /dev/null 2>&1; then
                        echo "APT is locked by another process. Waiting 30 seconds before retrying..."
                        if sudo lsof /var/lib/apt/lists/lock > /dev/null 2>&1; then
                            echo "Process holding apt lists lock:"
                            sudo lsof /var/lib/apt/lists/lock
                        fi
                        if sudo lsof /var/lib/dpkg/lock > /dev/null 2>&1; then
                            echo "Process holding dpkg lock:"
                            sudo lsof /var/lib/dpkg/lock
                        fi
                        sleep 30
                        ((attempt++))
                    else
                        apt_locked=false
                    fi
                done

                if $apt_locked; then
                    echo "Could not acquire apt lock after $max_attempts attempts."
                    echo "You may need to manually fix the lock issue with:"
                    echo "  sudo rm /var/lib/apt/lists/lock"
                    echo "  sudo rm /var/lib/dpkg/lock"
                    echo "  sudo rm /var/lib/dpkg/lock-frontend"
                    echo "WARNING: Only use these commands if you're sure no apt process is running!"
                    echo "Try installing tmux manually with: sudo apt-get install tmux"
                    return 1
                fi

                # Proceed with installation
                sudo apt-get update && sudo apt-get install -y tmux
            elif command -v dnf &> /dev/null; then
                echo "Detected dnf package manager"
                sudo dnf install -y tmux
            elif command -v yum &> /dev/null; then
                echo "Detected yum package manager"
                sudo yum install -y tmux
            elif command -v pacman &> /dev/null; then
                echo "Detected pacman package manager"
                sudo pacman -S --noconfirm tmux
            elif command -v zypper &> /dev/null; then
                echo "Detected zypper package manager"
                sudo zypper install -y tmux
            else
                echo "No supported package manager found. Please install tmux manually."
                return 1
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command -v brew &> /dev/null; then
                echo "Detected Homebrew package manager"
                brew install tmux
            elif command -v port &> /dev/null; then
                echo "Detected MacPorts package manager"
                sudo port install tmux
            else
                echo "No supported package manager found on macOS."
                echo "Please install Homebrew (https://brew.sh/) or MacPorts, then run this script again."
                return 1
            fi
        elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            # Windows with Git Bash or similar
            echo "Windows detected. Please install tmux manually or use WSL."
            return 1
        elif [[ "$OSTYPE" == "freebsd"* ]]; then
            # FreeBSD
            sudo pkg install -y tmux
        else
            echo "Unsupported operating system: $OSTYPE"
            return 1
        fi

        # Verify installation
        if ! command -v tmux &> /dev/null; then
            echo "Failed to install tmux. Please install it manually."
            echo "Checking if we can continue without tmux..."
            return 1
        else
            echo "tmux installed successfully."
            return 0
        fi
    else
        echo "tmux is already installed."
        return 0
    fi
}

# Function to check if we can continue without tmux
can_continue_without_tmux() {
    # Check for alternative terminal multiplexers
    if command -v screen &> /dev/null; then
        echo "Found 'screen' as an alternative to tmux. Would you like to use it instead? (y/n)"
        read -r use_screen
        if [[ "$use_screen" == "y" ]]; then
            echo "Will use 'screen' instead of tmux."
            USE_SCREEN=true
            return 0
        fi
    fi

    echo "This script can run multiple services without terminal multiplexing, but you'll need to open separate terminals."
    echo "Would you like to continue? (y/n)"
    read -r continue_without

    if [[ "$continue_without" == "y" ]]; then
        echo "Continuing without terminal multiplexing."
        return 0
    else
        echo "Exiting as requested."
        return 1
    fi
}

# Function to check if virtual environment exists and create if needed
check_virtual_env() {
    local venv_dir="$1"
    local venv_activate="$2" 
    local requirements="$3"

    if [[ ! -f "$venv_activate" ]]; then
        echo "Virtual environment not found at $venv_dir, creating..."
        # Check if python3 is installed
        if command -v python3 &> /dev/null; then
            python3 -m venv "$venv_dir"
        elif command -v python &> /dev/null; then
            python -m venv "$venv_dir"
        else
            echo "Python not found. Please install Python 3."
            exit 1
        fi
    fi

    # Check if requirements file exists
    if [[ ! -f "$requirements" ]]; then
        echo "Warning: Requirements file ($requirements) not found."
    fi
}

# Function to check and install Bun if needed
check_and_install_bun() {
    if ! command -v bun &> /dev/null; then
        echo "Bun not found. Would you like to install it? (y/n)"
        read -r install_bun

        if [[ "$install_bun" != "y" ]]; then
            echo "Skipping Bun installation."
            return 1
        fi

        echo "Installing Bun..."

        if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # macOS or Linux
            if command -v curl &> /dev/null; then
                curl -fsSL https://bun.sh/install | bash
                # Source the updated profile to make bun available in the current session
                if [[ -f "$HOME/.bashrc" ]]; then
                    source "$HOME/.bashrc"
                elif [[ -f "$HOME/.zshrc" ]]; then
                    source "$HOME/.zshrc"
                fi
                # Also try to export the PATH directly
                export PATH="$HOME/.bun/bin:$PATH"
            elif command -v wget &> /dev/null; then
                wget -qO- https://bun.sh/install | bash
                # Source the updated profile to make bun available in the current session
                if [[ -f "$HOME/.bashrc" ]]; then
                    source "$HOME/.bashrc"
                elif [[ -f "$HOME/.zshrc" ]]; then
                    source "$HOME/.zshrc"
                fi
                # Also try to export the PATH directly
                export PATH="$HOME/.bun/bin:$PATH"
            else
                echo "Neither curl nor wget found. Please install either curl or wget first, then run this script again."
                echo "Checking for alternative JS runtimes..."
                return 1
            fi
        elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            # Windows - prefer wget
            if command -v wget &> /dev/null; then
                wget -qO- https://bun.sh/install | bash
            elif command -v curl &> /dev/null; then
                curl -fsSL https://bun.sh/install | bash
            else
                echo "Neither wget nor curl found. Please install either wget or curl first, then run this script again."
                echo "Checking for alternative JS runtimes..."
                return 1
            fi
        else
            echo "Unsupported operating system for automatic Bun installation."
            echo "Please install Bun manually: https://bun.sh/docs/installation"
            echo "Checking for alternative JS runtimes..."
            return 1
        fi

        # Try to find bun in its installation directory if it's not in PATH
        if ! command -v bun &> /dev/null; then
            if [[ -f "$HOME/.bun/bin/bun" ]]; then
                echo "Found Bun at $HOME/.bun/bin/bun"
                export PATH="$HOME/.bun/bin:$PATH"
            fi
        fi

        # Verify installation
        if ! command -v bun &> /dev/null; then
            echo "Failed to install Bun. Please install it manually: https://bun.sh/docs/installation"
            echo "Checking for alternative JS runtimes..."
            return 1
        else
            echo "Bun installed successfully."
            return 0
        fi
    else
        echo "Bun is already installed."
        return 0
    fi
}

# Function to determine the best available JS runtime/package manager
detect_js_runtime() {
    # Prefer Bun if available
    if command -v bun &> /dev/null; then
        echo "bun"
        return
    fi

    # Check if Bun is installed but not in PATH
    if [[ -f "$HOME/.bun/bin/bun" ]]; then
        export PATH="$HOME/.bun/bin:$PATH"
        echo "bun"
        return
    fi

    # Check for other package managers in order of preference
    if command -v pnpm &> /dev/null; then
        echo "pnpm"
        return
    fi

    if command -v yarn &> /dev/null; then
        echo "yarn"
        return
    fi

    if command -v npm &> /dev/null; then
        echo "npm"
        return
    fi

    echo "none"
}

# Function to start frontend service
start_frontend() {
    echo "Starting Frontend service..."
    cd "$FRONTEND_DIR" || exit 1
    case "$JS_RUNTIME" in
        "bun")
            bun install && bun run build && bun start
            ;;
        "pnpm")
            pnpm install && pnpm run build && pnpm start
            ;;
        "yarn")
            yarn install && yarn build && yarn start
            ;;
        "npm")
            npm install && npm run build && npm start
            ;;
    esac
}

# Function to start backend service 
start_backend() {
    echo "Starting Backend service..."
    cd "$BACKEND_DIR" || exit 1 
    source "$BACKEND_VENV" && pip install -r requirements.txt && python main.py
}

# Function to start server service
start_server() {
    echo "Starting Server service..."
    cd "$SERVER_DIR" || exit 1
    case "$JS_RUNTIME" in
        "bun")
            bun install && bun start
            ;;
        "pnpm")
            pnpm install && pnpm start
            ;;
        "yarn")
            yarn install && yarn start
            ;;
        "npm")
            npm install && npm start
            ;;
    esac
}

# Function to start ML service
start_ml() {
    echo "Starting ML service..."
    cd "$ML_DIR" || exit 1
    source "$ML_VENV" && pip install -r requirements.txt && python train.py
}

# Function to start all services without tmux
start_all_with_bg() {
    echo "Starting all services in background. Press Ctrl+C to stop all services."

    # Create a temp directory for log files
    mkdir -p /tmp/mono_repo_logs

    # Start each service in background
    (cd "$FRONTEND_DIR" && case "$JS_RUNTIME" in
        "bun") bun install && bun run build && bun start;;
        "pnpm") pnpm install && pnpm run build && pnpm start;;
        "yarn") yarn install && yarn build && yarn start;;
        "npm") npm install && npm run build && npm start;;
    esac) > /tmp/mono_repo_logs/frontend.log 2>&1 &
    FRONTEND_PID=$!

    (cd "$BACKEND_DIR" && source "$BACKEND_VENV" && pip install -r requirements.txt && python main.py) > /tmp/mono_repo_logs/backend.log 2>&1 &
    BACKEND_PID=$!

    (cd "$SERVER_DIR" && case "$JS_RUNTIME" in
        "bun") bun install && bun start;;
        "pnpm") pnpm install && pnpm start;;
        "yarn") yarn install && yarn start;;
        "npm") npm install && npm start;;
    esac) > /tmp/mono_repo_logs/server.log 2>&1 &
    SERVER_PID=$!

    (cd "$ML_DIR" && source "$ML_VENV" && pip install -r requirements.txt && python train.py) > /tmp/mono_repo_logs/ml.log 2>&1 &
    ML_PID=$!

    echo "All services started with PIDs:"
    echo "Frontend: $FRONTEND_PID"
    echo "Backend: $BACKEND_PID"
    echo "Server: $SERVER_PID"
    echo "ML: $ML_PID"

    echo "Logs are being written to /tmp/mono_repo_logs/"
    echo "To view logs in real-time, open a new terminal and run: tail -f /tmp/mono_repo_logs/*.log"

    # Function to handle script termination
    cleanup() {
        echo "Stopping all services..."
        kill $FRONTEND_PID $BACKEND_PID $SERVER_PID $ML_PID 2>/dev/null
        wait
        echo "All services stopped."
        exit 0
    }

    # Set up the trap for clean exit
    trap cleanup SIGINT SIGTERM

    # Keep script running
    echo "Press Ctrl+C to stop all services"
    tail -f /tmp/mono_repo_logs/*.log
}

# Function to run all services with GNU Screen
start_all_with_screen() {
    SESSION="mono_repo"

    # Kill any existing session
    screen -X -S $SESSION quit 2>/dev/null

    # Start a new screen session
    screen -dmS $SESSION

    # Start frontend
    screen -S $SESSION -X screen -t "frontend"
    screen -S $SESSION -p "frontend" -X stuff "cd $FRONTEND_DIR && case "$JS_RUNTIME" in
        "bun") bun install && bun run build && bun start;;
        "pnpm") pnpm install && pnpm run build && pnpm start;;
        "yarn") yarn install && yarn build && yarn start;;
        "npm") npm install && npm run build && npm start;;
    esac\n"

    # Start backend
    screen -S $SESSION -X screen -t "backend"
    screen -S $SESSION -p "backend" -X stuff "cd $BACKEND_DIR && source $BACKEND_VENV && pip install -r requirements.txt && python main.py\n"

    # Start server
    screen -S $SESSION -X screen -t "server"
    screen -S $SESSION -p "server" -X stuff "cd $SERVER_DIR && case "$JS_RUNTIME" in
        "bun") bun install && bun start;;
        "pnpm") pnpm install && pnpm start;;
        "yarn") yarn install && yarn start;;
        "npm") npm install && npm start;;
    esac\n"

    # Start ML
    screen -S $SESSION -X screen -t "ml"
    screen -S $SESSION -p "ml" -X stuff "cd $ML_DIR && source $ML_VENV && pip install -r requirements.txt && python train.py\n"

    # Display a message
    echo "Starting mono repo development environment with screen..."
    echo "Using $JS_RUNTIME as JavaScript runtime"
    echo "Use 'screen -r $SESSION' to reconnect if detached."

    # Attach to the session
    screen -r $SESSION
}

# Set default values
USE_TMUX=false
USE_SCREEN=false

# Define project paths
PROJECT_ROOT=$(pwd)
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"
SERVER_DIR="$PROJECT_ROOT/server"
ML_DIR="$PROJECT_ROOT/ml"

# Define virtual environment paths
BACKEND_VENV_DIR="${BACKEND_VENV_DIR:-$BACKEND_DIR/venv}"
ML_VENV_DIR="${ML_VENV_DIR:-$ML_DIR/venv}"
BACKEND_VENV="$BACKEND_VENV_DIR/bin/activate"
ML_VENV="$ML_VENV_DIR/bin/activate"

# Check if directories exist
for dir in "$FRONTEND_DIR" "$BACKEND_DIR" "$SERVER_DIR" "$ML_DIR"; do
    if [[ ! -d "$dir" ]]; then
        echo "Warning: Directory $dir does not exist."
        echo "Would you like to create it? (y/n)"
        read -r create_dir
        if [[ "$create_dir" == "y" ]]; then
            mkdir -p "$dir"
            echo "Created $dir"
        else
            echo "Skipping $dir"
        fi
    fi
done

# Check virtual environments
check_virtual_env "$BACKEND_VENV_DIR" "$BACKEND_VENV" "$BACKEND_DIR/requirements.txt"
check_virtual_env "$ML_VENV_DIR" "$ML_VENV" "$ML_DIR/requirements.txt"

# Attempt to install Bun (preferred runtime)
check_and_install_bun

# Determine JS runtime to use
JS_RUNTIME=$(detect_js_runtime)
echo "Using $JS_RUNTIME as JavaScript runtime"

if [[ "$JS_RUNTIME" == "none" ]]; then
    echo "No JavaScript runtime found. Please install Bun (preferred), npm, yarn, or pnpm."
    exit 1
fi

# Main menu
while true; do
    clear
    echo "============================================"
    echo "      Mono Repo Development Environment     "
    echo "============================================"
    echo "Available services:"
    echo "1) Frontend"
    echo "2) Backend"
    echo "3) Server"
    echo "4) ML"
    echo "5) All services"
    echo "6) Configure"
    echo "7) Exit"
    echo "============================================"
    echo "Current settings:"
    echo "- JavaScript runtime: $JS_RUNTIME"
    if $USE_TMUX; then
        echo "- Terminal multiplexer: tmux"
    elif $USE_SCREEN; then
        echo "- Terminal multiplexer: screen"
    else
        echo "- Terminal multiplexer: none"
    fi
    echo "============================================"

    read -r -p "Select an option: " menu_choice

    case $menu_choice in
        1)
            start_frontend
            ;;
        2)
            start_backend
            ;;
        3)
            start_server
            ;;
        4)
            start_ml
            ;;
        5)
            # Start all services
            if $USE_TMUX; then
                # Using tmux
                SESSION="mono_repo"

                # Kill any existing session
                tmux kill-session -t $SESSION 2>/dev/null

                # Create a new session
                tmux new-session -d -s $SESSION

                # Start frontend
                tmux rename-window -t $SESSION "frontend"
                case "$JS_RUNTIME" in
                    "bun")
                        tmux send-keys -t $SESSION "cd $FRONTEND_DIR && bun install && bun run build && bun start" C-m
                        ;;
                    "pnpm")
                        tmux send-keys -t $SESSION "cd $FRONTEND_DIR && pnpm install && pnpm run build && pnpm start" C-m
                        ;;
                    "yarn")
                        tmux send-keys -t $SESSION "cd $FRONTEND_DIR && yarn install && yarn build && yarn start" C-m
                        ;;
                    "npm")
                        tmux send-keys -t $SESSION "cd $FRONTEND_DIR && npm install && npm run build && npm start" C-m
                        ;;
                esac

                # Start backend (Python)
                tmux new-window -t $SESSION -n "backend"
                tmux send-keys -t $SESSION "cd $BACKEND_DIR && source $BACKEND_VENV && pip install -r requirements.txt && python main.py" C-m

                # Start server
                tmux new-window -t $SESSION -n "server"
                case "$JS_RUNTIME" in
                    "bun")
                        tmux send-keys -t $SESSION "cd $SERVER_DIR && bun install && bun start" C-m
                        ;;
                    "pnpm")
                        tmux send-keys -t $SESSION "cd $SERVER_DIR && pnpm install && pnpm start" C-m
                        ;;
                    "yarn")
                        tmux send-keys -t $SESSION "cd $SERVER_DIR && yarn install && yarn start" C-m
                        ;;
                    "npm")
                        tmux send-keys -t $SESSION "cd $SERVER_DIR && npm install && npm start" C-m
                        ;;
                esac

                # Start ML (Python)
                tmux new-window -t $SESSION -n "ml"
                tmux send-keys -t $SESSION "cd $ML_DIR && source $ML_VENV && pip install -r requirements.txt && python train.py" C-m

                # Set default window to frontend
                tmux select-window -t $SESSION:0

                # Display a message
                echo "Starting mono repo development environment with tmux..."
                echo "Using $JS_RUNTIME as JavaScript runtime"
                echo "Use 'tmux attach-session -t $SESSION' to reconnect if detached."

                # Attach to the session
                tmux attach-session -t $SESSION
            elif $USE_SCREEN; then
                start_all_with_screen
            else
                start_all_with_bg
            fi
            ;;
        6)
            # Configuration submenu
            while true; do
                clear
                echo "============================================"
                echo "            Configuration Menu              "
                echo "============================================"
                echo "1) Change JavaScript runtime"
                echo "2) Toggle terminal multiplexer"
                echo "3) Back to main menu"
                echo "============================================"

                read -r -p "Select an option: " config_choice

                case $config_choice in
                    1)
                        echo "Select JavaScript runtime:"
                        echo "1) Bun (recommended)"
                        echo "2) pnpm"
                        echo "3) yarn"
                        echo "4) npm"

                        read -r -p "Select runtime: " runtime_choice

                        case $runtime_choice in
                            1)
                                if command -v bun &> /dev/null; then
                                    JS_RUNTIME="bun"
                                else
                                    check_and_install_bun && JS_RUNTIME="bun"
                                fi
                                ;;
                            2)
                                if command -v pnpm &> /dev/null; then
                                    JS_RUNTIME="pnpm"
                                else
                                    echo "pnpm not found. Please install it first."
                                    read -p "Press Enter to continue..."
                                fi
                                ;;
                            3)
                                if command -v yarn &> /dev/null; then
                                    JS_RUNTIME="yarn"
                                else
                                    echo "yarn not found. Please install it first."
                                    read -p "Press Enter to continue..."
                                fi
                                ;;
                            4)
                                if command -v npm &> /dev/null; then
                                    JS_RUNTIME="npm"
                                else
                                    echo "npm not found. Please install it first."
                                    read -p "Press Enter to continue..."
                                fi
                                ;;
                            *)
                                echo "Invalid choice."
                                read -p "Press Enter to continue..."
                                ;;
                        esac
                        ;;
                    2)
                        echo "Select terminal multiplexer:"
                        echo "1) tmux (recommended)"
                        echo "2) screen"
                        echo "3) none (use background processes)"

                        read -r -p "Select multiplexer: " multi_choice

                        case $multi_choice in
                            1)
                                if command -v tmux &> /dev/null; then
                                    USE_TMUX=true
                                    USE_SCREEN=false
                                else
                                    check_and_install_tmux && USE_TMUX=true && USE_SCREEN=false
                                fi
                                ;;
                            2)
                                if command -v screen &> /dev/null; then
                                    USE_TMUX=false
                                    USE_SCREEN=true
                                else
                                    echo "screen not found. Please install it first."
                                    read -p "Press Enter to continue..."
                                fi
                                ;;
                            3)
                                USE_TMUX=false
                                USE_SCREEN=false
                                ;;
                            *)
                                echo "Invalid choice."
                                read -p "Press Enter to continue..."
                                ;;
                        esac
                        ;;
                    3)
                        break
                        ;;
                    *)
                        echo "Invalid choice."
                        read -p "Press Enter to continue..."
                        ;;
                esac
            done
            ;;
        7)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid choice."
            read -p "Press Enter to continue..."
            ;;
    esac
done