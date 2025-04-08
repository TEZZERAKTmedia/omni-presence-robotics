import React, { useRef, useState, useEffect } from "react";

export default function FloorPlanEditor() {
  const [imageSrc, setImageSrc] = useState(null);
  const [binaryGrid, setBinaryGrid] = useState(null);
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });

  const imageCanvasRef = useRef(null);
  const boundaryCanvasRef = useRef(null);
  const containerRef = useRef(null);

  // 1. Upload image
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      console.log("✅ Image loaded into memory.");
      setImageSrc(reader.result);
    };
    reader.readAsDataURL(file);
  };

  // 2. Draw image and compute grid
  const drawImageToCanvas = () => {
    const canvas = imageCanvasRef.current;
    const ctx = canvas.getContext("2d");
    const img = new Image();

    img.onload = () => {
      const scale = Math.min(
        containerRef.current.clientWidth / img.width,
        containerRef.current.clientHeight / img.height
      );

      const width = Math.floor(img.width * scale);
      const height = Math.floor(img.height * scale);
      canvas.width = width;
      canvas.height = height;
      setCanvasSize({ width, height });

      ctx.clearRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);
      console.log(`🖼️ Image drawn at ${width}x${height}`);
      computeBinaryGrid(ctx, width, height);
    };

    img.src = imageSrc;
  };

  useEffect(() => {
    if (imageSrc) drawImageToCanvas();
  }, [imageSrc]);

  // 3. Binary map from pixels
  const computeBinaryGrid = (ctx, width, height) => {
    const imageData = ctx.getImageData(0, 0, width, height);
    const pixels = imageData.data;
    const grid = [];
    let darkCount = 0;

    for (let y = 0; y < height; y++) {
      const row = [];
      for (let x = 0; x < width; x++) {
        const i = (y * width + x) * 4;
        const [r, g, b] = [pixels[i], pixels[i + 1], pixels[i + 2]];
        const brightness = (r + g + b) / 3;
        const isWall = brightness < 220; // More lenient threshold
        row.push(isWall ? 1 : 0);
        if (isWall) darkCount++;
      }
      grid.push(row);
    }

    setBinaryGrid(grid);
    console.log(`📊 Binary grid: ${height} rows x ${grid[0].length} cols`);
    console.log(`🧱 Wall pixels: ${darkCount}`);
  };

  // 4. Draw only the edge of black areas
  const drawBoundaryMap = () => {
    if (!binaryGrid) return;

    const { width, height } = canvasSize;
    const canvas = boundaryCanvasRef.current;
    const ctx = canvas.getContext("2d");

    canvas.width = width;
    canvas.height = height;
    ctx.clearRect(0, 0, width, height);

    let edgeCount = 0;
    ctx.fillStyle = "#00f5d4"; // Cyan/green for contrast

    for (let y = 1; y < height - 1; y++) {
      for (let x = 1; x < width - 1; x++) {
        if (binaryGrid[y][x] === 1) {
          const top = binaryGrid[y - 1][x];
          const bottom = binaryGrid[y + 1][x];
          const left = binaryGrid[y][x - 1];
          const right = binaryGrid[y][x + 1];
          if ([top, bottom, left, right].some((v) => v === 0)) {
            ctx.fillRect(x, y, 1, 1);
            edgeCount++;
          }
        }
      }
    }

    console.log(`🧭 Drawn ${edgeCount} edge pixels on boundary canvas`);
  };

  return (
    <div className="w-full min-h-screen bg-black text-white flex flex-col items-center p-4">
      <input
        type="file"
        accept="image/*"
        onChange={handleFileUpload}
        className="mb-4"
      />

      {imageSrc && (
        <button
          onClick={drawBoundaryMap}
          className="mb-6 px-4 py-2 bg-green-700 rounded"
        >
          Generate Vector Map
        </button>
      )}

      <div ref={containerRef} className="w-full max-w-4xl h-[300px] border mb-4">
        <canvas ref={imageCanvasRef} className="w-full h-full" />
      </div>

      <h2 className="text-xl font-bold mb-2">🧭 Boundary Vector Map</h2>
      <div className="border bg-neutral-900 p-2">
        <canvas ref={boundaryCanvasRef} />
      </div>
    </div>
  );
}
