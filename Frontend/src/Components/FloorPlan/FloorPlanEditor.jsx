import React, { useRef, useState, useEffect } from "react";

export default function FloorPlanEditor() {
  const [imageSrc, setImageSrc] = useState(null);
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });
  const canvasRef = useRef(null);
  const containerRef = useRef(null);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setImageSrc(reader.result);
    reader.readAsDataURL(file);
  };

  const drawImage = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const img = new Image();

    img.onload = () => {
      const scale = Math.min(
        containerRef.current.clientWidth / img.width,
        containerRef.current.clientHeight / img.height
      );

      const width = img.width * scale;
      const height = img.height * scale;

      canvas.width = width;
      canvas.height = height;
      setImageSize({ width, height });

      ctx.clearRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);
    };

    img.src = imageSrc;
  };

  useEffect(() => {
    if (imageSrc) drawImage();
  }, [imageSrc]);

  const generateFromImage = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const { width, height } = canvas;

    const imageData = ctx.getImageData(0, 0, width, height);
    const pixels = imageData.data;

    const map = []; // binary grid: 1 = open (white), 0 = wall (black)

    for (let y = 0; y < height; y++) {
      const row = [];
      for (let x = 0; x < width; x++) {
        const i = (y * width + x) * 4;
        const [r, g, b] = [pixels[i], pixels[i + 1], pixels[i + 2]];
        const isWhite = r > 200 && g > 200 && b > 200;
        row.push(isWhite ? 1 : 0);
      }
      map.push(row);
    }

    const visited = Array.from({ length: height }, () => Array(width).fill(false));
    const regions = [];

    const floodFill = (sx, sy) => {
      const queue = [[sx, sy]];
      const region = [];
      let minX = sx,
        minY = sy,
        maxX = sx,
        maxY = sy;

      while (queue.length) {
        const [x, y] = queue.pop();
        if (
          x < 0 || y < 0 || x >= width || y >= height ||
          visited[y][x] || map[y][x] === 0
        )
          continue;

        visited[y][x] = true;
        region.push([x, y]);
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);

        queue.push([x + 1, y]);
        queue.push([x - 1, y]);
        queue.push([x, y + 1]);
        queue.push([x, y - 1]);
      }

      return { region, bounds: { minX, minY, maxX, maxY } };
    };

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        if (!visited[y][x] && map[y][x] === 1) {
          const { region, bounds } = floodFill(x, y);
          if (region.length > 500) {
            regions.push(bounds);
          }
        }
      }
    }

    drawImage(); // Redraw base image first

    // Draw detected regions
    ctx.strokeStyle = "red";
    ctx.lineWidth = 2;
    regions.forEach(({ minX, minY, maxX, maxY }) => {
      ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);
    });

    console.log("Detected regions:", regions);
  };

  return (
    <div className="w-full h-[90vh] flex flex-col items-center justify-center">
      <input
        type="file"
        accept="image/*"
        onChange={handleFileUpload}
        className="mb-4"
      />
      {imageSrc && (
        <button
          onClick={generateFromImage}
          className="mb-4 px-4 py-2 bg-green-600 text-white rounded"
        >
          Auto Generate Map from Image
        </button>
      )}
      <div
        ref={containerRef}
        className="relative w-full max-w-6xl h-[70vh] border border-gray-400"
      >
        <canvas ref={canvasRef} className="w-full h-full" />
      </div>
    </div>
  );
}
