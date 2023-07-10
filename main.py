import numpy as np
from skimage import transform as tf
from moviepy.editor import *
from moviepy.video.compositing.CompositeVideoClip import ColorClip

# Set up movie constants. We are defining the width of the movie,
# calculating the height to maintain a 16:9 aspect ratio, defining the movie size,
# speed of the text scrolling, duration of the video and the frames per second.
w = 720
h = w * 9 // 16
moviesize = w, h
txt_speed = 24
duration = 60
fps = 30


def main():
    # Create the Star Wars logo
    logo = create_star_wars_logo()

    # Create the scrolling text
    txt = create_scroll_text()

    # Create a TextClip object from the scrolling text
    clip_txt = create_text_image(txt)

    # Create moving text from the TextClip
    moving_txt = scroll_text_image(clip_txt)

    # Warp the text to give a perspective of distance
    warped_txt = create_warped_text(moving_txt)

    # Create the background image
    stars = ImageClip('bg.jpg')

    # Darken the background image
    stars_darkened = darken_image(stars)

    # Load the audio file
    music = AudioFileClip('song.mp3')

    # Composite the movie with the logo, darkened background and the warped text
    final_clip = compose_movie_with_logo(logo, stars_darkened, warped_txt)

    # Set the audio to the movie
    final_with_audio = set_audio_to_movie(music, final_clip)

    # Write the final movie to a file
    write_to_file(final_with_audio, "Star Wars Intro.mp4")


def darken_image(stars):
    # Darken the background image by multiplying each pixel by 0.6 and converting the values to integers
    return stars.fl_image(lambda pic: (0.6 * pic).astype('int16'))


def create_star_wars_logo():
    # Load the logo image, resize it to the height of the movie, set its position to center and duration to 3 seconds
    logo = (ImageClip("star_wars_logo.png").resize(height=h).set_position("center").set_duration(3))

    # Apply a crossfadeout transition to the logo
    logo = logo.crossfadeout(1)

    # Resize the logo over time to create a shrink effect
    return logo.resize(lambda t: max(1 - 0.5 * t, 0.1))


def create_scroll_text():
    # Create the scrolling text with 10 newline characters at the beginning and end for spacing
    return 10 * "\n" + create_text() + 10 * "\n"


def create_text():
    # Define the story text as a formatted string.
    # This text will be displayed in the opening crawl.
    # It includes a placeholder for the user's name.
    return "\n".join([
        "A long time ago, in a galaxy far, far away...",
        "The Star Wars saga unfolds, with tales of",
        "tragedy and heartbreak that leave a lingering",
        "sadness in their wake.",
        "",
        "Darth Vader, once a promising Jedi Knight, now",
        "consumed by the darkness, roams the galaxy as",
        "a symbol of lost innocence and broken trust.",
        "",
        "Obi-Wan Kenobi, a seasoned Jedi Master, carries",
        "the weight of past failures on his weary shoulders.",
        "Regret fills his heart as he reflects on battles",
        "lost and friendships shattered.",
        "",
        "The galaxy, torn by endless conflict, bears the",
        "scars of war. Planets ravaged, families torn apart,",
        "and dreams crushed under the oppressive rule of the",
        "Empire. A somber reminder of the cost of freedom.",
        "",
        "In every corner of the galaxy, hope flickers like",
        "a dying star. The memories of better days, the",
        "laughter and camaraderie, now distant echoes that",
        "fade with each passing moment.",
        "",
        f"And amidst the darkness, a new glimmer emerges.",
        f"A young Jedi, known as Xander Drakon, rises",
        "from the shadows, their destiny entwined with",
        "the fate of the universe. Will they have the",
        "strength to wield the Force and bring balance",
        "to the galaxy once more?",
        "",
        "And so, the Star Wars saga continues, a tale of",
        "sadness and resilience, reminding us that even in",
        "the face of overwhelming darkness, the smallest",
        "spark of hope can ignite a new dawn.",
        "",
        "",
        "",
    ])


def create_text_image(txt):
    # Create a TextClip object from the text, set color, alignment, font size, font, and rendering method
    return TextClip(txt, color='cyan', align='Center', fontsize=25, font='Xolonium-Bold', method='label')


def scroll_text_image(clip_txt):
    # Create a blank clip of the same size as the text clip and composite them together
    # The scroll effect is created by dynamically changing the cropping area of the composite clip
    blank = create_blank_clip(clip_txt)
    composited_clip = CompositeVideoClip([blank, clip_txt.set_position(("center", "bottom"))])
    start_scroll = h / 2 + txt_speed * 2
    fl = lambda gf, t: gf(t)[int(txt_speed * t + start_scroll):int(txt_speed * t + start_scroll) + h, :]
    return composited_clip.fl(fl, apply_to=['mask'])


def create_blank_clip(clip_txt):
    # Create a black blank clip of the same size and duration as the text clip
    blank = ColorClip((clip_txt.size[0], clip_txt.size[1] + h), col=(0, 0, 0)).set_opacity(0)
    return blank.set_duration(clip_txt.duration)


def create_warped_text(moving_txt):
    # Warp the text into a trapezoid shape to give a perspective of distance
    fl_im = lambda pic: trapzWarp(pic, 0.2, 0.3)
    fl_mask = lambda pic: trapzWarp(pic, 0.2, 0.3, ismask=True)
    warped_txt = moving_txt.fl_image(fl_im)
    warped_txt.mask = warped_txt.mask.fl_image(fl_mask)
    return warped_txt


def compose_movie_with_logo(logo, bg, txt):
    # Create the final movieclip by compositing the darkened background, the moving text (starting from 2 seconds into the video) and the logo, then setting the total duration of the movie.
    return CompositeVideoClip([bg, txt.set_position(('center', 'bottom')).set_start(2), logo],
                              size=moviesize).set_duration(duration)


def set_audio_to_movie(music, movie):
    # Set the audio track to the movie.
    # The audio is a subclip from the original audio, starting 0.3 seconds in and lasting for the duration of the movie.
    # The audio volume is reduced to 80%, and it fades out over the last 5 seconds.
    music = music.subclip(0.3, 0.3 + duration).volumex(0.8).audio_fadeout(5)
    return movie.set_audio(music)


def write_to_file(movie, filename):
    # Write the final movie to a file with the specified filename at 30 frames per second,
    # using the H.264 codec for the video and AAC for the audio.
    movie.write_videofile(filename, fps=fps, codec='libx264', audio_codec="aac")


def trapzWarp(pic, cx, cy, ismask=False):
    # This function applies a trapezoid warp to an image.
    # It uses a Projective Transform from the skimage library to map source coordinates to destination coordinates.
    # The coordinates are defined such that the trapezoid has its shorter base at the top of the image.
    # The parameters cx and cy control the positions of the vertices of the trapezoid.
    Y, X = pic.shape[:2]
    if Y == 0:
        return np.zeros((h, X, 3), dtype='uint8') if not ismask else np.zeros((h, X))

    src = np.array([[0, 0], [X, 0], [X, Y], [0, Y]])
    dst = np.array([[cx * X, cy * Y], [(1 - cx) * X, cy * Y], [X, Y], [0, Y]])
    tform = tf.ProjectiveTransform()
    tform.estimate(src, dst)
    im = tf.warp(pic, tform.inverse, output_shape=(Y, X))
    return im if ismask else (im * 255).astype('uint8')


if __name__ == '__main__':
    main()
