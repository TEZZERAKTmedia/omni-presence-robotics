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
