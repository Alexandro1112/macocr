# TextRecognitionMacOs
Simple utility for recognizing text on an image, supports many languages!

▎Usage

Here's a quick example of how to use recog_lib to recognize text from an image:

```
import TextRecognitionMacOs

# Create an instance of the Recognition class
sh = TextRecognitionMacOs.Recognition(img='/Users/aleksandr/russian_text.jpeg',
                                   output_format='coord')

print(sh.return_results())

```

▎Parameters

• image_path: The path to the image file from which you want to extract text.

• output_format: Specify the desired output format it may be ``coord`` if we want return coordinates of text, or ``text`` if we want return text.







<br><br>Also you can print coordinates and text, use format ``text+coord``. Here's example

```
import TextRecognitionMacOs

# Create an instance of the Recognition class
r = speech_recognition.Recognition('/Users/aleksandr/russian_text.jpeg', 'text+coord')

dictionary = r.return_results()
text = dictionary['text']
coordinates = dictionary['coord']
# Match text and coordinates.
data = {}
for key, value in zip(text, coordinates):
    data[key] = value

print(data)
```
