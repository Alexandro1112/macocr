# TextRecognitionMacOs
Simple utility for recognizing text on an image, supports many languages!

▎Usage

Here's a quick example of how to use recog_lib to recognize text from an image:

```
import TextRecognitionMacOs as rc


rec = rc.Recognition(
    img='/Users/aleksandr/Desktop/screenshot.png',
    lang='ru-RU',
    output_format='text',
    use_CPU=True,
)
print(rec.return_results())
```

Parameters

• image_path: The path to the image file from which you want to extract text.

• output_format: Specify the desired output format it may be ``coord`` <br> if we want return coordinates of text, or ``text`` if we want return text.







<br><br>Also you can print coordinates and text, use format ``text+coord``. Here's example

```

import TextRecognitionMacOs as rc

params = 'text+coord'
for i in params.split('+'):
    rec = rc.Recognition(
        img='/Users/aleksandr/Desktop/screenshot.png',
        lang='ru-RU',
        output_format=i,
        use_CPU=True,
        recognition_interest=[
            (0, 0), (0.5, 0.5)
        ]
    )
    print(rec.return_results())
```
