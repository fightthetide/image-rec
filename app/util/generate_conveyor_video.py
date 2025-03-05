import cv2
import numpy as np
import random
import os
from pathlib import Path
from collections import Counter

# Video settings
width, height = 640, 480  # Resolution
fps = 30                  # Frames per second
min_duration = 120         # Minimum duration in seconds
output_file = "conveyor_test_with_images.mp4"

# Conveyor belt settings
belt_height = height // 2  # Belt occupies bottom half
belt_color = (100, 100, 100)  # Gray color for belt
belt_speed = 5  # Pixels per frame the belt moves

# Directory with stock images
stock_image_dir = Path("util/stock_images")  # Adjust this path as needed
if not stock_image_dir.exists():
    raise FileNotFoundError(f"Directory '{stock_image_dir}' not found. Please create it and add images.")

# Load stock images and map to their names
stock_images = {}
for img_path in stock_image_dir.glob("*.jpg"):  # Supports .jpg; add .png, etc., if needed
    img = cv2.imread(str(img_path))
    if img is not None:
        item_name = img_path.stem  # e.g., "dog" from "dog.jpg"
        stock_images[item_name] = img
if not stock_images:
    raise ValueError(f"No valid images found in '{stock_image_dir}'.")

# Item settings
max_items_per_frame = 10  # Max items visible at once
max_scale = 0.5  # Max scale factor for images (relative to frame size)

# Calculate transit time (frames needed for an item to cross the screen)
transit_frames = (width + 100) // belt_speed  # +100 for safety (fully off-screen)
spawn_deadline = transit_frames  # Last frame where new items can spawn

# Initialize video duration (will adjust based on last item)
total_frames = max(min_duration * fps, spawn_deadline + transit_frames)

# Create video writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

# Track items across frames and tally
items = []  # List of (x, y, item_name, image, scale, angle)
item_tally = Counter()  # Count occurrences of each item type

for frame_num in range(total_frames):
    # Create a blank frame
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Draw conveyor belt
    frame[belt_height:, :] = belt_color

    # Randomly add new items (only before spawn_deadline)
    # if frame_num < spawn_deadline and random.random() < 0.1 and len(items) < max_items_per_frame:
    if random.random() < 0.1 and len(items) < max_items_per_frame:
        item_name = random.choice(list(stock_images.keys()))
        stock_img = stock_images[item_name]
        # scale = random.uniform(0.05, max_scale)  # Random scale between 5% and 20%
        scale = max_scale
        angle = random.randint(0, 360)  # Random orientation
        # Random vertical position within belt (ensure item fits)
        img_height = int(stock_img.shape[0] * scale)
        y_min = belt_height + 10  # Small padding from top of belt
        y_max = height - img_height - 10  # Padding from bottom
        y = random.randint(y_min, max(y_min, y_max))  # Random y within belt
        items.append([width, y, item_name, stock_img, scale, angle])  # Start at right edge
        item_tally[item_name] += 1  # Increment tally

    # Update and draw existing items
    new_items = []
    for item in items:
        x, y, item_name, stock_img, scale, angle = item
        x -= belt_speed  # Move item left

        # Resize image based on scale
        img_height, img_width = stock_img.shape[:2]
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        resized_img = cv2.resize(stock_img, (new_width, new_height))

        # Rotate image
        rot_mat = cv2.getRotationMatrix2D((new_width // 2, new_height // 2), angle, 1)
        rotated_img = cv2.warpAffine(resized_img, rot_mat, (new_width, new_height))

        # Overlay image on frame (handle boundaries)
        if x + new_width > 0 and x < width and y + new_height <= height and y >= belt_height:
            roi = frame[y:y + new_height, max(0, x):min(width, x + new_width)]
            img_roi = rotated_img[:, max(0, -x):min(new_width, width - x)]
            if img_roi.shape[:2] == roi.shape[:2]:  # Ensure shapes match
                mask = cv2.cvtColor(img_roi, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
                mask_inv = cv2.bitwise_not(mask)
                roi_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
                roi_fg = cv2.bitwise_and(img_roi, img_roi, mask=mask)
                frame[y:y + new_height, max(0, x):min(width, x + new_width)] = cv2.add(roi_bg, roi_fg)

        # Keep item if it’s still partially on screen
        if x + new_width > 0:
            new_items.append([x, y, item_name, stock_img, scale, angle])

    items = new_items  # Update items list

    # Write frame to video
    out.write(frame)

# Release the video writer
out.release()

# Output the tally and final duration
final_duration = total_frames / fps
print(f"Video saved as {output_file} (Duration: {final_duration:.1f} seconds)")
print("\nItem Tally:")
for item_name, count in item_tally.items():
    print(f"{item_name}: {count}")
