import argparse
import os
from recog_lib import Recognition


def main():
    parser = argparse.ArgumentParser(description='Text Recognition Command Line Tool')

    parser.add_argument('--img', type=str, required=True, help='Path to the image file')
    parser.add_argument('--lang', type=str, default='en-US', help='Language for recognition')
    parser.add_argument('--img_orientation', type=str, default='up', help='Orientation of the image (e.g., up, down)')
    parser.add_argument('--output_format', type=str, default='text', help='Output format(e.g., text, coord, confidence)')

    # Recognition interest should be passed as a list of tuples
    args = parser.parse_args()

    if os.path.exists(args.img):

        # Create Recognition instance
        recognizeText = Recognition(
            img=args.img,
            lang=args.lang,
            img_orientation=args.img_orientation,
            output_format=args.output_format

        )

        # Get results
        results = recognizeText.return_results()
        print(results)
    else:
        print(f'{args.img} not exist!')


main()
