# /usr/bin/python
import inspect
import Vision
import Quartz
import Cocoa
import re
from typing import Dict, SupportsFloat, SupportsInt, List, AnyStr, Tuple, Literal
import numpy
import objc
import cv2
from collections.abc import Iterable
import io
from PIL import Image


class Recognition:
    """
    The class creates a recognition object that takes:

    :argument img: The path to the desired image cannot contain Cyrillic characters. Assign the path to the image or the
    filename, if it is located in the same directory.

    :argument output_format:
    explanation of what we need to return: text, if we need the text from the image. coordinate,
    if we need to get the coordinates of the text, certain, if we need to get the accuracy of the recognized text
    in floating point values.

    :argument lang: the language of text recognition, if the text contains more than 2 languages, leave lang to "en-US"

    :argument use_CPU: This method (or property) allows you to specify that text recognition should be performed only on
     the central processing unit (CPU), and not on the graphics processing unit (GPU). This can be useful in
    certain scenarios, for example, when it is important to reduce the load on the hardware resources of the device.

    :argument recognize_interest: argument accepts a dict with coordinates, this is necessary to limit text recognition
    by x, y, width and height coordinates. Default values: (0, 0), (1, 1).

    :argument img_orientation: changes the orientation of the image, which is applied before the image is initialized
    with VNRecognizeTextRequest.

    :argument **args accepts functions that belong to the VNRecognizeTextRequest class to manually change
     and add any parameters.

    :argument recognize_level: parameter that sets the recognition speed, can be 1 or 0.
    0 - more accurate recognition,
    1 - faster, but has low quality.

    """
    def __getattr__(self, item):
        try:
            metadata = item.__metadata__()['arguments']
            signature = b''.join(item['type'] for item in metadata)
            # b'@:@' mean that function return object not equal None;
            if b'@:@' not in signature or all(signature in symbols for symbols in objc.splitSignature(b'@:@')):
                raise ValueError
        except AttributeError:
            raise AttributeError('Can not get access to %s' % repr(item))

    def __init__(self,
                 img: str,
                 img_orientation='default',
                 output_format: Literal['text', 'coord', 'confidence'] | Iterable = 'text',
                 lang='en-US',
                 use_CPU: bool=None,
                 recognition_interest: List[Tuple[float | int, float | int]] = None,
                 recognition_level=0,
                 **args
                 ) -> None:

        self.info = output_format
        self.lang = lang
        self.use_CPU = use_CPU
        self.levels = {
            0: Vision.VNRequestTextRecognitionLevelAccurate,
            1: Vision.VNRequestTextRecognitionLevelFast
            }

        self.orientations = {
            'default': 0,
            'up': Quartz.kCGImagePropertyOrientationUp,
            'down': Quartz.kCGImagePropertyOrientationDown,
            'left': Quartz.kCGImagePropertyOrientationLeft,
            'right': Quartz.kCGImagePropertyOrientationRight,
            'right-mirrored': Quartz.kCGImagePropertyOrientationRightMirrored,
            'left-mirrored': Quartz.kCGImagePropertyOrientationLeftMirrored,
            'up-mirrored': Quartz.kCGImagePropertyOrientationUpMirrored,
            'down-mirrored': Quartz.kCGImagePropertyOrientationDownMirrored,
        }

        def completion_handler_(request, error):
            """
            Create handler for accept recognized text.
            """
            if error is not None:
                raise Exception(error)
            del error

            self.all = {}
            self.output_txt = []
            self.output_crd = []
            self.output_cnf = []

            def multiply_list(values):
                """convert CGPoint to list with coordinates(x, y, width, and height)."""
                for i in range(len(values)):
                    bound_box = [_xy for _xy in
                                 (values[i].x, values[i].y, values.size.width, values.size.height)]
                    if isinstance(img, str):
                        x, y, w, h = bound_box
                        x_1 = x * self.width
                        y_2 = (1 - y) * self.height
                        x_2 = w * self.width
                        y_1 = h * self.height

                        return x_1, y_2, x_2, y_1

                    elif isinstance(img, numpy.ndarray):

                        x, y, w, h = bound_box
                        x_1 = x * img.shape[1]
                        y_2 = (1 - y) * img.shape[0]
                        x_2 = w * img.shape[1]
                        y_1 = h * img.shape[0]

                        return x_1, y_2, x_2, y_1

            if not isinstance(request.results(), Iterable) and recognition_interest is not None:
                self.output_txt.append([])
                # If we limit text recognition by coordinates, and if nothing is found at the
                # given coordinates, then we return an empty dictionary.
                return

            for result in request.results():
                if isinstance(result, Vision.VNRecognizedTextObservation):
                    for text in result.topCandidates_(1):
                        if len(self.info.split('+')) < 3:

                            if 'text' in self.info.split('+'):
                                self.output_txt.append(text.string())
                                self.all = {}

                            if 'coord' in self.info.split('+'):
                                self.output_crd.append(multiply_list(result.boundingBox()))
                                self.all = {}

                            elif 'confidence' in self.info.split('+'):
                                self.output_cnf.append(text.confidence())
                                self.all = {}

                        elif all(word in self.info for word in ['text', 'coord', 'confidence']):
                            self.output_txt.append(text.string())
                            self.output_crd.append(multiply_list(result.boundingBox()))
                            self.output_cnf.append(result.confidence())
                            self.all.update({
                                    'coord': self.output_crd,
                                    'text': self.output_txt,
                                    'confidence': self.output_cnf
                            })

                        else:
                            return None

        def recognize(file) -> None:
            """
            The recognize function processes an image file to recognize text using the PyObjC framework. It validates
             the file path for Cyrillic characters, initializes image handling, sets recognition parameters,
              and manages errors during the recognition process.
            """
            try:
                orient = self.orientations[img_orientation]
            except KeyError:
                raise ValueError(
                    f'Orientation must be {repr((*self.orientations.keys(),))}'
                )

            if isinstance(file, str):
                if bool(var := re.search(r'[а-яА-ЯёЁ]', file)):
                    raise SyntaxError(
                        f'The path to the file must\'t contain Cyrillic characters started on {var.start() + 1!r}.'
                    )
                try:
                    image = Vision.NSImage.alloc().initWithContentsOfFile_(
                        Cocoa.CFSTR(file)).TIFFRepresentation()
                    size = Vision.NSImage.alloc().initWithContentsOfFile_(Cocoa.CFSTR(img)).size()

                    self.width = int(size.width)
                    self.height = int(size.height)

                except AttributeError:
                    raise FileNotFoundError(f'Failed to load image {img.__repr__()}') from None

                cg = Cocoa.NSBitmapImageRep.imageRepWithData_(
                    image
                ).CGImage()

                req_handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_orientation_options_(
                    cg, orient, None
                )

            elif isinstance(file, numpy.ndarray):
                def numpy_array_to_ns_data(image_array):
                    """Convert a NumPy array to NSData."""
                    pil_image = Image.fromarray(image_array)
                    with io.BytesIO() as output:
                        pil_image.save(output, format='PNG', save_all=True)
                        data = output.getvalue()
                    return Cocoa.NSData.dataWithBytes_length_(data, len(data))

                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

                image_bytes = numpy_array_to_ns_data(rgb)

                ns_data_image = Cocoa.NSData.dataWithBytes_length_(image_bytes, len(image_bytes))

                req_handler = Vision.VNImageRequestHandler.alloc().initWithData_orientation_options_(
                    ns_data_image, orient, None)
            else:
                raise TypeError('Image can be a NumPy array with data of image, or path to file.')

            self.request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(completion_handler_)
            self.request.setRevision_error_(Vision.VNRecognizeTextRequestRevision3, None)

            if recognition_interest is not None:
                try:
                    self.request.setRegionOfInterest_(
                        Cocoa.CGRect(*recognition_interest)
                    )
                except objc._objc.internal_error:
                    raise ValueError(f'recognition_interest has wrong type or values.')

            elif recognition_interest is None:
                self.request.setRegionOfInterest_(
                    Cocoa.CGRect((0, 0), (1, 1))
                    # Set as region of searching at all image. This described there
                    # https://developer.apple.com/documentation/dockkit/dockaccessory/setregionofinterest(_:)/
                )
            else:
                raise ValueError(
                    'recognition_interest has wrong type or values.'
                )

            if not self.lang == 'en-US':
                self.request.setRecognitionLanguages_(lang)

            if self.use_CPU is True:
                self.request.setUsesCPUOnly_(Vision.kCFBooleanTrue) # noqa

            if recognition_level is not None:
                self.request.setRecognitionLevel_(self.levels[recognition_level] if not (1 or 0) else 0)

            if args:
                for (keys, values) in args.items():
                    if keys in self.request.__dir__():
                        # pass name of attribute and type of returned value, for example we need to get value from
                        # function recognitionLevel, so we pass recognitionLevel, and type (int)

                        # text = macosr.Recognition(
                        #   img='textocr.png',
                        #    lang='en-US',
                        #    use_CPU=True,
                        #    recognition_level=1,
                        #    recognitionLevel=int
                        # )
                        # print(text.recognitionLevel) # 1

                        if len(inspect.signature(eval(f'self.request.{keys}')).parameters) == 0:
                            # if function only return value and didn't accept arguments
                            _value = eval(
                                'self.request.%s()' % keys
                            )
                            setattr(self, keys, values(_value))

                        elif len(inspect.signature(eval(f'self.request.{keys}')).parameters) > 1:
                            method = f'self.request.%s('
                            for i in range(len(values)):
                                method += '%s, '
                            method += ')'
                            eval(method % (keys, *values))
                    else:
                        raise AttributeError

            with objc.autorelease_pool():
                req_handler.performRequests_error_([self.request], None) # noqa

        recognize(img)

    def return_results(self) -> Dict[AnyStr, SupportsInt] | List[SupportsFloat]:
        """I created this method because when we try to return any data through a handle, we get an error.
         The Objc method cannot return or save any values."""

        if not self.all:
            try:
                return [sublist for sublist in
                        [self.output_txt, self.output_crd, self.output_cnf] if sublist]
            except IndexError:
                return []
        return self.all

    def text_lang(self):
        return self.request.recognitionLanguages()

    @property
    def supported_languages(self):
        return self.request.supportedRecognitionLanguagesAndReturnError_(None)[0]

    def image_size(self):
        """return image width and height."""
        return [self.width, self.height]
