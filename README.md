# macocr
Simple utility for recognizing text on an image, supports many languages!

# For install macocr: 
1. Clone the repository:
   
   ```
   git clone https://github.com/Alexandro1112/macocr/
   ```
2 And go to the file
   ```
cd macocr
   ```
    
▎Usage recog_lib.py

Here's a quick example of how to use recog_lib to recognize text from an image:

```
import macocr as rc


rec = rc.Recognition(
    img='/Users/aleksandr/Desktop/screenshot.png',
    lang='ru-RU',
    output_format='text',
    use_CPU=True,
)
print(rec.return_results())
```

<h1>Parameters</h1>

• ``image_path``: The path to the image file from which you want to extract text.

• ``output_format``: Specify the desired output format it may be ``coord`` <br> if we want return coordinates of text, or ``text`` if we want return text.



<br>Also you can print coordinates and text, use format ``text+coord``. Here's example

```

import macocr as rc


rec = rc.Recognition(
    img='file2.png',
    lang='ru-RU',
    output_format='coord+text',
    use_CPU=True,

)

print(rec.return_results())

```
• ```img_oreintation``` You can change image orinetation, if image mirrored and you need make recognizable. 


<br> 


▎Usage recog_util.py

Run the tool from the command line with the following syntax:

```
python recog_util.py --img <path_to_image> --lang <language_code> --img_orientation <orientation> --output_format <format> --recognition_interest <coordinates>
```


▎Arguments

•  ```--img:``` (required) Path to the image file you want to process.<br>


• ``` --lang:``` (optional) Language for recognition (default: en-US).<br>


•  ```--img_orientation:``` (optional) Orientation of the image (default: up). Options include up, down, etc.<br>


•  ```--output_format:``` (optional) Output format for results (default: text). Options include text, coord, confidence.<br>


•  ```--recognition_interest:``` (optional) List of recognition interest coordinates as (x,y) pairs. Example: (0,0) (1,1).<br>

▎Example

To recognize text from an image located at image.jpg with English language support, you can run:

```
python recog_util.py --img image.jpg --lang en-US --img_orientation up --output_format text 
```

