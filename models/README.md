# YOLOv8 ONNX Model Placeholder

This directory contains AI models for edge inference on UAV platforms.

## Models

### yolov8n.onnx
- **Type**: Object Detection
- **Framework**: YOLOv8 (Ultralytics)
- **Format**: ONNX Runtime
- **Size**: ~6MB
- **Speed**: ~50 FPS on CPU
- **Use Case**: Real-time detection on UAVs

## How to Download Models

You can download pre-trained YOLOv8 models using the following methods:

### Method 1: Using Ultralytics Python Package

```bash
pip install ultralytics
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt').export(format='onnx')"
mv yolov8n.onnx models/
```

### Method 2: Download Pre-exported ONNX

```bash
# Download from Ultralytics GitHub releases
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.onnx -O models/yolov8n.onnx
```

### Method 3: Use Mock Model (Development)

For testing without a real model:

```bash
# Create a dummy ONNX file
touch models/yolov8n.onnx
```

The edge inference service will detect if it's a placeholder and run in simulation mode.

## Model Optimization

For production deployment, consider:

1. **TensorRT Optimization** (NVIDIA GPUs)
   ```bash
   trtexec --onnx=yolov8n.onnx --saveEngine=yolov8n.engine --fp16
   ```

2. **OpenVINO** (Intel Hardware)
   ```bash
   mo --input_model yolov8n.onnx --output_dir openvino/
   ```

3. **Quantization** (INT8 for edge devices)
   ```python
   from ultralytics import YOLO
   model = YOLO('yolov8n.pt')
   model.export(format='onnx', int8=True)
   ```

## Custom Training

To train on your own dataset:

```bash
# Prepare dataset in YOLO format
# dataset/
#   images/
#     train/
#     val/
#   labels/
#     train/
#     val/
#   data.yaml

yolo train model=yolov8n.pt data=dataset/data.yaml epochs=100 imgsz=640
yolo export model=runs/detect/train/weights/best.pt format=onnx
```

## Supported Classes

The default COCO-trained model detects 80 classes including:
- person
- car, truck, bus, motorcycle
- bicycle
- airplane
- boat
- And 73 more...

See `model_registry.yaml` for the complete list.

## Performance Benchmarks

| Model | Size | Speed (CPU) | mAP50 |
|-------|------|-------------|-------|
| YOLOv8n | 6 MB | 50 FPS | 37.3 |
| YOLOv8s | 22 MB | 30 FPS | 44.9 |
| YOLOv8m | 52 MB | 15 FPS | 50.2 |

For UAV edge deployment, YOLOv8n is recommended for balance of speed and accuracy.
