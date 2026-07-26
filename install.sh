#!/bin/bash

# Supercode Installation Script
# Usage: curl https://raw.githubusercontent.com/fishing-ainpm/supercode/master/install.sh | bash

set -e

echo "==================================="
echo "   Installing Supercode..."
echo "==================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3.8+ is installed
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}Python ${PYTHON_VERSION} found${NC}"

# Create installation directory
INSTALL_DIR="${HOME}/.local/supercode"
echo -e "${YELLOW}Installing to ${INSTALL_DIR}...${NC}"
mkdir -p "${INSTALL_DIR}"

# Clone or update the repository
if [ -d "${INSTALL_DIR}/.git" ]; then
    echo -e "${YELLOW}Updating existing installation...${NC}"
    cd "${INSTALL_DIR}"
    git pull origin master
else
    echo -e "${YELLOW}Cloning repository...${NC}"
    git clone https://github.com/fishing-ainpm/supercode.git "${INSTALL_DIR}"
    cd "${INSTALL_DIR}"
fi

# Create virtual environment
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
python3 -m venv "${INSTALL_DIR}/venv"
source "${INSTALL_DIR}/venv/bin/activate"

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
fi

# Create symlink in /usr/local/bin for easy access (optional)
if [ -f "supercode" ] || [ -f "supercode.py" ]; then
    echo -e "${YELLOW}Creating command symlink...${NC}"
    mkdir -p "${HOME}/.local/bin"
    
    if [ -f "supercode.py" ]; then
        cat > "${HOME}/.local/bin/supercode" << 'EOF'
#!/bin/bash
source "$HOME/.local/supercode/venv/bin/activate"
python3 "$HOME/.local/supercode/supercode.py" "$@"
EOF
    else
        cat > "${HOME}/.local/bin/supercode" << 'EOF'
#!/bin/bash
source "$HOME/.local/supercode/venv/bin/activate"
python3 -m supercode "$@"
EOF
    fi
    
    chmod +x "${HOME}/.local/bin/supercode"
    
    # Add to PATH if not already present
    if [[ ":$PATH:" != *":${HOME}/.local/bin:"* ]]; then
        echo -e "${YELLOW}Adding ${HOME}/.local/bin to PATH...${NC}"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "${HOME}/.bashrc"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "${HOME}/.zshrc" 2>/dev/null || true
        export PATH="${HOME}/.local/bin:$PATH"
    fi
fi

echo ""
echo -e "${GREEN}==================================="
echo "   Installation completed!"
echo "===================================${NC}"
echo ""
echo -e "${YELLOW}Installation directory:${NC} ${INSTALL_DIR}"
echo -e "${YELLOW}Virtual environment:${NC} ${INSTALL_DIR}/venv"
echo ""
echo "To use supercode, run:"
echo -e "${GREEN}  supercode --help${NC}"
echo ""
echo "To update your shell configuration, run:"
echo -e "${GREEN}  source ~/.bashrc${NC}"
echo ""
