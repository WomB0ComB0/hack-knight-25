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
            return 0
        fi
    fi

    echo "This script requires tmux (or an alternative) to run multiple services simultaneously."
    echo "Would you like to continue without terminal multiplexing? This will only start one service. (y/n)"
    read -r continue_without

    if [[ "$continue_without" == "y" ]]; then
        echo "Continuing without terminal multiplexing. Only one service will be started."
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
        echo "Bun not found. Installing..."

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

# Run tmux installation check
if ! check_and_install_tmux; then
    echo "Failed to install tmux."

    # Check if we can continue without tmux
    if ! can_continue_without_tmux; then
        exit 1
    fi

    USE_TMUX=false
else
    USE_TMUX=true
fi

# Attempt to install Bun (preferred runtime)
check_and_install_bun

# Define project paths
PROJECT_ROOT=$(pwd)
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"
SERVER_DIR="$PROJECT_ROOT/server"
ML_DIR="$PROJECT_ROOT/ml"

# Define virtual environment paths
BACKEND_VENV_DIR="$BACKEND_DIR/venv"
ML_VENV_DIR="$ML_DIR/venv"
BACKEND_VENV="$BACKEND_VENV_DIR/bin/activate"
ML_VENV="$ML_VENV_DIR/bin/activate"

# Check if directories exist
for dir in "$FRONTEND_DIR" "$BACKEND_DIR" "$SERVER_DIR" "$ML_DIR"; do
    if [[ ! -d "$dir" ]]; then
        echo "Error: Directory $dir does not exist."
        exit 1
    fi
done

# Check virtual environments
check_virtual_env "$BACKEND_VENV_DIR" "$BACKEND_VENV" "$BACKEND_DIR/requirements.txt"
check_virtual_env "$ML_VENV_DIR" "$ML_VENV" "$ML_DIR/requirements.txt"

# Determine JS runtime to use
JS_RUNTIME=$(detect_js_runtime)
echo "Using $JS_RUNTIME as JavaScript runtime"

if [[ "$JS_RUNTIME" == "none" ]]; then
    echo "No JavaScript runtime found. Please install Bun (preferred), npm, yarn, or pnpm."
    exit 1
fi

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
            tmux send-keys -t $SESSION "cd $FRONTEND_DIR && bun install && bun start" C-m
            ;;
        "pnpm")
            tmux send-keys -t $SESSION "cd $FRONTEND_DIR && pnpm install && pnpm start" C-m
            ;;
        "yarn")
            tmux send-keys -t $SESSION "cd $FRONTEND_DIR && yarn install && yarn start" C-m
            ;;
        "npm")
            tmux send-keys -t $SESSION "cd $FRONTEND_DIR && npm install && npm start" C-m
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
else
    # Not using tmux, ask which service to start
    echo "Which service would you like to start?"
    echo "1) Frontend"
    echo "2) Backend"
    echo "3) Server"
    echo "4) ml"

    read -r service_choice

    case $service_choice in
        1)
            echo "Starting Frontend service..."
            cd "$FRONTEND_DIR" || exit 1
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
            ;;
        2)
            echo "Starting Backend service..."
            cd "$BACKEND_DIR" || exit 1
            source "$BACKEND_VENV" && pip install -r requirements.txt && python main.py
            ;;
        3)
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
            ;;
        4)
            echo "Starting ML service..."
            cd "$ML_DIR" || exit 1
            source "$ML_VENV" && pip install -r requirements.txt && python train.py
            ;;
        *)
            echo "Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi