import sys, os
from PIL import Image

if len(sys.argv) < 2:
    print("Usage: python resize.py input.png")
    sys.exit(1)

input_image = sys.argv[1]
if os.path.isdir(input_image):
    print(f"Resizing all images in folder: {input_image}")
    images = [os.path.join(input_image, f) for f in os.listdir(input_image) if f.endswith('.png')]
else:
    assert input_image.endswith('.png'), "Only support PNG image"
    assert os.path.exists(input_image), f"File not found: {input_image}"
    images = [input_image]
n = len(images)
print(f"Found {n} images")

if len(sys.argv) > 2:
    size = int(sys.argv[2])
else:  
    size = 64

outdir = os.path.join(os.path.dirname(__file__), 'logo')
os.makedirs(outdir, exist_ok=True)

for i, file in enumerate(images, 1):
    print(f"Resizing {i}/{n}: {file}")

    # 打开图片
    image = Image.open(file)

    # 获取图片的原始尺寸
    width, height = image.size

    new_width = size
    new_height = size

    # 缩放图片
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 保存缩放后的图片
    output_image = os.path.join(outdir, os.path.basename(file))
    resized_image.save(output_image)
    print(f"Saved to {output_image}")

    # 显示缩放后的图片（可选）
    # resized_image.show()

