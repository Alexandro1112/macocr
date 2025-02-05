# TextRecognitionMacOs
Simple utility for recognizing text on an image, supports many languages!
▎Usage

Here's a quick example of how to use recog_lib to recognize text from an image:

```
import TextRecognitionMacOs

# Create an instance of the Recognition class
r = TextRecognitionMacOs.Recognition()

# Get information from the specified image
r.get_info_from_image('/Users/aleksandr/russian_text.jpeg', 'coord')

# Print the recognized results
print(r.return_results())
```

▎Parameters

• image_path: The path to the image file from which you want to extract text.

• output_format: Specify the desired output format it may be ``coord`` if we want return coordinates of text, or ``text`` if we want return text.
