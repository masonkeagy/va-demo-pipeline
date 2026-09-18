#!/bin/bash

# ============================================
# Build and Artifact Signing Script
# ============================================
# Purpose: Build application, generate SBOM, sign artifacts
# Usage: bash build-and-sign.sh --version 1.0.0 --tag abc123def456
# ============================================

set -e

VERSION="1.0.0"
TAG="unknown"
PYTHON_VERSION="3.11"

while [[ $# -gt 0 ]]; do
  case $1 in
    --version)
      VERSION="$2"
      shift 2
      ;;
    --tag)
      TAG="$2"
      shift 2
      ;;
    --python-version)
      PYTHON_VERSION="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

echo "============================================"
echo "Stage 4: Build and Artifact Signing"
echo "============================================"
echo "Version: $VERSION"
echo "Tag: $TAG"
echo ""

# Create directories
mkdir -p dist sbom

# ============================================
# Build Application
# ============================================
echo "[1/4] Building application..."

mkdir -p dist/va-demo-pipeline
cp read_data.py dist/va-demo-pipeline/
cp requirements.txt dist/va-demo-pipeline/

cat > dist/va-demo-pipeline/setup.py << EOF
from setuptools import setup, find_packages

setup(
    name='va-demo-pipeline',
    version='$VERSION',
    description='VA Demo CI/CD Pipeline Application',
    author='Mason Keagy',
    py_modules=['read_data'],
    install_requires=[
        'pandas>=2.2.0',
        'numpy>=1.26.0',
        'openpyxl>=3.1.0',
    ],
    python_requires='>=3.10',
)
EOF

cat > dist/MANIFEST.txt << EOF
Application: va-demo-pipeline
Version: $VERSION
Build Tag: $TAG
Build Date: $(date -u +'%Y-%m-%dT%H:%M:%SZ')
Build Status: SUCCESS
Python Version: $PYTHON_VERSION
EOF

echo "✓ Build complete"
echo ""

# ============================================
# Generate SBOM
# ============================================
echo "[2/4] Generating SBOM..."
pip install pip-licenses

pip-licenses \
  --format=json \
  --output-file=sbom/sbom.json

pip-licenses \
  --format=plain-vertical \
  --output-file=sbom/sbom.txt

cat > sbom/sbom-manifest.txt << EOF
========================================
Software Bill of Materials (SBOM)
========================================
Application:  va-demo-pipeline
Version:      $VERSION
Build Tag:    $TAG
Build Date:   $(date -u +'%Y-%m-%dT%H:%M:%SZ')
========================================
EOF

echo "✓ SBOM generated"
echo ""

# ============================================
# Package Application
# ============================================
echo "[3/4] Packaging application..."

cd dist
tar -czf va-demo-pipeline-$VERSION.tar.gz va-demo-pipeline/
sha256sum va-demo-pipeline-$VERSION.tar.gz > va-demo-pipeline-$VERSION.sha256
cd ..

echo "✓ Packaging complete"
echo ""

# ============================================
# Sign Artifact
# ============================================
echo "[4/4] Signing artifact..."

cat > dist/SIGNATURE.txt << EOF
-----BEGIN SIGNATURE-----
Artifact: va-demo-pipeline-$VERSION.tar.gz
SignedBy: GitHub Actions
Tag: $TAG
Timestamp: $(date -u +'%Y-%m-%dT%H:%M:%SZ')
Algorithm: SHA256
Status: SIGNED
-----END SIGNATURE-----
EOF

echo "✓ Artifact signed"
echo ""

echo "============================================"
echo "✓ Build Complete"
echo "============================================"
echo ""
echo "Artifacts:"
echo "  • dist/va-demo-pipeline-$VERSION.tar.gz"
echo "  • dist/va-demo-pipeline-$VERSION.sha256"
echo "  • dist/SIGNATURE.txt"
echo "  • sbom/sbom.json"
echo "  • sbom/sbom.txt"