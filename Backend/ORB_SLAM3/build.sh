#!/bin/bash
cd "$(dirname "$0")"

set -e  # Stop on first error

# Detect OpenCV path via Homebrew (macOS)
OPENCV_DIR=$(brew --prefix opencv)/lib/cmake/opencv4
export OpenCV_DIR=$OPENCV_DIR
echo "[BUILD] OpenCV_DIR set to $OpenCV_DIR"

echo "[BUILD] Building Thirdparty/DBoW2 ..."
cd Thirdparty/DBoW2
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
cd ../../../

echo "[BUILD] Building Thirdparty/g2o ..."
cd Thirdparty/g2o
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
cd ../../../

echo "[BUILD] Building Thirdparty/Sophus ..."
cd Thirdparty/Sophus
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
cd ../../../

echo "[BUILD] Extracting vocabulary ..."
cd Vocabulary

if [ ! -f ORBvoc.txt ]; then
  if [ ! -f ORBvoc.txt.tar.gz ]; then
    echo "[INFO] ORBvoc.txt.tar.gz not found. Downloading from source..."
    curl -L -o ORBvoc.txt.tar.gz https://raw.githubusercontent.com/raulmur/ORB_SLAM2/master/Vocabulary/ORBvoc.txt.tar.gz
  fi

  # Verify checksum BEFORE extraction
  echo "[INFO] Verifying vocabulary archive..."
  EXPECTED_HASH="cd16e7d02ab0e146c165e43084324e8c3b8c0b60e419b9f9b6701f503f1ef0a2"
  DOWNLOADED_HASH=$(shasum -a 256 ORBvoc.txt.tar.gz | awk '{print $1}')

  if [ "$DOWNLOADED_HASH" != "$EXPECTED_HASH" ]; then
    echo "[ERROR] ORBvoc.txt.tar.gz hash mismatch! Download may be corrupted."
    exit 1
  fi

  echo "[INFO] Extracting ORBvoc.txt.tar.gz..."
  tar -xf ORBvoc.txt.tar.gz
else
  echo "[INFO] Vocabulary already extracted."
fi

cd ..


echo "[BUILD] Building ORB_SLAM3 main library ..."
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Ensure stereo_tum binary exists
if [ -f Examples/Stereo/stereo_tum ]; then
  echo "[✅ DONE] stereo_tum built successfully!"
else
  echo "[❌ ERROR] stereo_tum was not built. Please check CMakeLists.txt"
fi


echo "[✅ DONE] ORB_SLAM3 built successfully."
