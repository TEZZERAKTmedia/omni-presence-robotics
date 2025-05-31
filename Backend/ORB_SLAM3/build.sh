#!/bin/bash
cd "$(dirname "$0")"
set -e

# Function to detect and clear invalid CMake cache
check_and_clean_cache() {
  BUILD_DIR=$1
  EXPECTED_SOURCE=$2
  CACHE_FILE="$BUILD_DIR/CMakeCache.txt"

  if [ -f "$CACHE_FILE" ]; then
    ACTUAL_SOURCE=$(grep CMAKE_HOME_DIRECTORY "$CACHE_FILE" | cut -d= -f2)
    if [ "$ACTUAL_SOURCE" != "$EXPECTED_SOURCE" ]; then
      echo "[INFO] Cache mismatch detected in $BUILD_DIR"
      echo "       Expected: $EXPECTED_SOURCE"
      echo "       Found:    $ACTUAL_SOURCE"
      echo "       Cleaning build directory..."
      rm -rf "$BUILD_DIR"
    fi
  fi
}

# Detect platform and OpenCV path
if command -v brew &> /dev/null; then
  OPENCV_DIR=$(brew --prefix opencv)/lib/cmake/opencv4
  echo "[BUILD] OpenCV_DIR set via Homebrew: $OPENCV_DIR"
else
  OPENCV_DIR="/usr/lib/x86_64-linux-gnu/cmake/opencv4"
  echo "[BUILD] OpenCV_DIR set for Linux: $OPENCV_DIR"
fi

export OpenCV_DIR=$OPENCV_DIR

COMMON_FLAGS="-DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS='-Wno-error -Wno-array-bounds'"

# Build Thirdparty/DBoW2
echo "[BUILD] Building Thirdparty/DBoW2 ..."
cd Thirdparty/DBoW2
check_and_clean_cache build "$(pwd)"
mkdir -p build && cd build
cmake .. $COMMON_FLAGS
make -j$(nproc)
cd ../../../

# Build Thirdparty/g2o
echo "[BUILD] Building Thirdparty/g2o ..."
cd Thirdparty/g2o
check_and_clean_cache build "$(pwd)"
mkdir -p build && cd build
cmake .. $COMMON_FLAGS
make -j$(nproc)
cd ../../../

# Build Thirdparty/Sophus WITHOUT TESTS
echo "[BUILD] Building Thirdparty/Sophus (skipping tests) ..."
cd Thirdparty/Sophus
check_and_clean_cache build "$(pwd)"
mkdir -p build && cd build
cmake .. $COMMON_FLAGS -DBUILD_TESTS=OFF
make -j$(nproc)
cd ../../../

# Vocabulary
echo "[BUILD] Extracting vocabulary ..."
cd Vocabulary
if [ ! -f ORBvoc.txt ]; then
  if [ ! -f ORBvoc.txt.tar.gz ]; then
    echo "[INFO] ORBvoc.txt.tar.gz not found. Downloading..."
    curl -L -o ORBvoc.txt.tar.gz https://raw.githubusercontent.com/raulmur/ORB_SLAM2/master/Vocabulary/ORBvoc.txt.tar.gz
  fi

  echo "[INFO] Verifying archive..."
  EXPECTED_HASH="cd16e7d02ab0e146c165e43084324e8c3b8c0b60e419b9f9b6701f503f1ef0a2"
  DOWNLOADED_HASH=$(shasum -a 256 ORBvoc.txt.tar.gz | awk '{print $1}')
  if [ "$DOWNLOADED_HASH" != "$EXPECTED_HASH" ]; then
    echo "[ERROR] Vocabulary hash mismatch!"
    exit 1
  fi

  echo "[INFO] Extracting vocabulary..."
  tar -xf ORBvoc.txt.tar.gz
else
  echo "[INFO] Vocabulary already extracted."
fi
cd ..

# Main ORB_SLAM3 build
echo "[BUILD] Building ORB_SLAM3 ..."
check_and_clean_cache build "$(pwd)"
mkdir -p build && cd build
cmake .. $COMMON_FLAGS
make -j$(nproc)

# Confirm build
if [ -f Examples/Stereo/stereo_tum ]; then
  echo "[✅ DONE] stereo_tum built successfully!"
else
  echo "[❌ ERROR] stereo_tum not found. Check logs above."
fi

echo "[✅ DONE] ORB_SLAM3 built successfully."
