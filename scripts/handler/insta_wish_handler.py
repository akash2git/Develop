from scripts.wish_logger import get_logger
# from scripts import cursor
import os
import tempfile
from scripts import client, username
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

logger = get_logger()
TEMP_DIR = tempfile.gettempdir()

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Birthday Email</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
        }

        .neuomorphic-card {
            background-color: #f5f5f5;
            border-radius: 10px;
            box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.1), 0 0 5px rgba(0, 0, 0, 0.1);
            padding: 20px;
            width: 80%;
            margin: 20px auto;
        }

        .neuomorphic-button {
            background-color: #f5f5f5;
            border: none;
            border-radius: 5px;
            box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.1), 0 0 2px rgba(0, 0, 0, 0.1);
            padding: 10px 20px;
            cursor: pointer;
            color: #333;
        }

        .neuomorphic-button:hover {
            background-color: #e5e5e5;
        }
    </style>
</head>
<body>
    <div class="neuomorphic-card">
        <h2>Happy Birthday</h2>
        <p>$message$</p>
        <img src="cid:image1" alt="Photo" width="300">
    </div>
</body>
</html>
"""


def login_handler(payload):
    final_json = {"status": False, "message": "Invalid username or password", "users": []}
    try:
        users = []
        if payload.username == 'admin' and payload.password == 'admin':
            final_json["status"] = True
            final_json["message"] = "Logged in successfully"
    except Exception as e:
        logger.exception("Exception while logged in: {}".format(e))
    return final_json


def create_birthday_frame(image_path, frame_num, text_color, sparkle_color):
    # Load image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Add "Happy Birthday" text
    font = ImageFont.truetype("montez.ttf", 60)
    text = "Happy Birthday!"

    # Calculate text width and height using textbbox
    textbbox = draw.textbbox((0, 0), text, font=font)
    textwidth = textbbox[2] - textbbox[0]
    textheight = textbbox[3] - textbbox[1]

    width, height = image.size
    text_x = (width - textwidth) // 2
    text_y = height - textheight - 50

    # Animate the text by making it pulse
    size_factor = 1 + 0.1 * np.sin(frame_num / 5)  # Simple pulsing effect
    draw.text((text_x, text_y), text, font=font, fill=text_color)

    # Add balloons at random positions
    for i in range(5):
        balloon_x = random.randint(50, width - 50)
        balloon_y = random.randint(50, height // 2)
        draw.ellipse((balloon_x, balloon_y, balloon_x + 50, balloon_y + 100),
                     fill=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))

    # Add glitter at random positions
    for i in range(100):
        glitter_x = random.randint(0, width)
        glitter_y = random.randint(0, height)
        draw.ellipse((glitter_x, glitter_y, glitter_x + 3, glitter_y + 3), fill=sparkle_color)

    return image


def create_birthday_gif(image_path, output_gif_path, num_frames=30):
    frames = []
    text_color = (255, 255, 0)  # Bright yellow text
    sparkle_color = (255, 255, 255)  # White sparkles

    for frame_num in range(num_frames):
        frame = create_birthday_frame(image_path, frame_num, text_color, sparkle_color)
        frames.append(frame)

    # Save as GIF
    frames[0].save(output_gif_path, save_all=True, append_images=frames[1:], duration=100, loop=0)


def upload_data(insta_id, text, image, video):
    final_json = {"status": False, "message": "Failed to upload data"}
    try:
        image_content = image.file.read() if image else None
        video_content = video.file.read() if video else None

        # Retrieve Instagram ID from the database securely
        # insta_id = None
        # if cursor is not None:
        #     cursor.execute("SELECT insta_id FROM users WHERE name=?", (users[0],))
        #     response = cursor.fetchall()
        #     insta_id = response[0][0] if response else None

        if insta_id is not None:
            recipient_username = insta_id

            # Get Instagram IDs for the recipient and sender
            user_id = client.user_id_from_username(username)  # Sender
            recipient_id = client.user_id_from_username(recipient_username)  # Recipient

            # Check mutual following status
            following = client.user_following(user_id)
            followers = client.user_followers(user_id)

            they_follow = recipient_id in followers
            you_follow = recipient_id in following

            logger.debug(f"Recipient {recipient_username} follows you: {they_follow}")
            logger.debug(f"You follow recipient {recipient_username}: {you_follow}")

            # user_info = client.user_info_by_username(recipient_username)
            client.direct_send(text, [int(recipient_id)])
            logger.info(f"Text message sent to {recipient_username}")

            if image_content:
                image_temp_path = os.path.join(TEMP_DIR, "temp_image.jpg")
                with open(image_temp_path, "wb") as f:
                    f.write(image_content)

                # client.direct_send_photo(Path(gif_temp_path), [int(recipient_id)])
                client.direct_send_file(Path(image_temp_path), [int(recipient_id)])
                logger.info(f"Photo sent to {recipient_username}")
                os.remove(image_temp_path)

            if video_content:
                video_temp_path = os.path.join(TEMP_DIR, "temp_video.mp4")
                with open(video_temp_path, "wb") as f:
                    f.write(video_content)

                client.direct_send_video(Path(video_temp_path), [int(recipient_id)])
                logger.info(f"Video sent to {recipient_username}")
                os.remove(video_temp_path)

            final_json["status"] = True
            final_json["message"] = "Message sent successfully"
        else:
            logger.error(f"No Instagram ID found for user {insta_id}")

    except Exception as e:
        logger.exception(f"Error while sending media: {e}")

    return final_json


def send_email_data(cc_email, image, recipient_email, message):
    final_json = {
        "status": False,
        "message": "Failed to send email"
    }
    try:
        msg = MIMEMultipart()
        msg['From'] = "akashselvaraj121@gmail.com"
        msg['To'] = recipient_email
        msg['Cc'] = cc_email
        msg['Subject'] = "Birthday Wish"

        # Attach the body with HTML content
        msg.attach(MIMEText(html_content.replace("$message$", message), 'html'))
        image_content = image.file.read()
        if image_content:
            image_temp_path = os.path.join(TEMP_DIR, "temp_image.jpg")
            gif_temp_path = os.path.join(TEMP_DIR, "temp_gif.gif")
            with open(image_temp_path, "wb") as f:
                f.write(image_content)
            create_birthday_gif(image_temp_path, gif_temp_path)
            with open(gif_temp_path, 'rb') as img_attachment:
                image = MIMEImage(img_attachment.read())
                image.add_header('Content-ID', '<image1>')  # Use cid for embedding in HTML
                msg.attach(image)

            # SMTP session
            try:
                # Gmail SMTP server
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login("akashselvaraj121@gmail.com", 'nsjv ught bcth dbzo')  # Replace 'your_password' with the actual password
                text = msg.as_string()
                server.sendmail("akashselvaraj121@gmail.com", recipient_email, text)
                logger.debug("Email sent successfully!")
                final_json["status"] = True
                final_json["message"] = "Mail sent successfully"
            except Exception as e:
                logger.exception(f"Failed to send email: {e}")
            finally:
                server.quit()
            os.remove(image_temp_path)
            os.remove(gif_temp_path)
    except Exception as e:
        logger.exception("Exception: {}".format(e))
    return final_json
