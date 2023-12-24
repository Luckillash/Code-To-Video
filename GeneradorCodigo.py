from pygments import highlight
from pygments.lexers.python import Python3Lexer
from pygments.formatters import ImageFormatter
from pygments.styles import get_style_by_name
import moviepy.editor as mp
from rich.progress import Progress

def center_on_canvas(image_path, canvas_size=(1080, 1920)):
    img_clip = mp.ImageClip(image_path)

    margin = 60
    max_width = canvas_size[0] - 2 * margin
    max_height = canvas_size[1] - 2 * margin

    if img_clip.size[0] > max_width or img_clip.size[1] > max_height:
        img_clip = img_clip.resize(width=max_width)

    x_center = (canvas_size[0] - img_clip.size[0]) // 2
    y_center = (canvas_size[1] - img_clip.size[1]) // 2
    position = (x_center, y_center)

    canvas = mp.ColorClip(size=canvas_size, color=(255, 255, 255))
    centered_clip = mp.CompositeVideoClip([canvas, img_clip.set_position(position)])

    centered_clip.save_frame(image_path)

    return image_path

formatter_options = {
    "style": get_style_by_name('monokai'),
    "font_size": 32
}

with open('index.html', 'r') as file:

    code = file.read()

filenames = [f"datos/{i}.png" for i in range(len(code) + 1)]
filenames_cleaned = []

with Progress() as progress:
    task1 = progress.add_task("[red]Creating images", total=(len(code) + 1))
    
    while not progress.finished:
        for idx, filename in enumerate(filenames):
            if code[idx-1].isspace():
                progress.update(task1, advance=1)
                continue
            
            with open(filename, "wb") as image_file:
                highlight(
                    code[0:idx],
                    Python3Lexer(),
                    ImageFormatter(**formatter_options),
                    image_file
                )

                center_on_canvas(filename)
                filenames_cleaned.append(filename)
                progress.update(task1, advance=1)

print("Generating clips and duration")

clips = [mp.ImageClip(filename).set_duration(0.05) for filename in filenames_cleaned]
clips[-1] = clips[-1].set_duration(10)

print("Concatenating videoclips")

final_clip = mp.concatenate_videoclips(clips, method="compose")
final_clip.write_videofile("code_animation.mp4", fps=24, codec="libx264")
