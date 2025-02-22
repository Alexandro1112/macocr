# /usr/bin/python
import inspect
import Vision
import Quartz
import Cocoa
import re
from typing import Dict, SupportsFloat, SupportsInt, List, AnyStr, Tuple, Literal
import objc
from collections.abc import Iterable


class Recognition:
    """
    Class create Recognition object which accept:

    :argument img: The path to the desired image cannot contain Cyrillic characters. Assign an image path or file name
    if it is in the same directory.

    :argument output_format:
    an explanation of what we need to return: text if we need text from the image. coordinate,
    if we need to get the coordinates of the text, confidence if we need to get the accuracy of the recognized text
    in floating point values.

    :argument lang: language of recognition text, if text contain more 2 languages keep lang at ``en-US``.

    :argument use_CPU: This method (or property) allows you to specify that text recognition should be performed only on
     the central processing unit (CPU) rather than on the graphics processing unit (GPU). This can be useful in
     certain scenarios, for example, when it is important to reduce the load on the device's hardware resources.

    :argument recognition_interest: argument accept dict with coordinates, this is need for a limit text recognition by
    x, y, width and height coordinates. Default values: (0, 0), (1, 1).

    :argument img_orientation: change the image orientation, which is applied before the image is initialized
    using VNRecognizeTextRequest.

    :argument **args accept object isinstance to Vision.VNRecognizeTextRequest for using function from self. Pass None
     if function doesn't accept anything.

    """
    def __getattr__(self, item):
        try:
            metadata = item.__metadata__()['arguments']
            signature = b''.join(item['type'] for item in metadata)
            # b'@:@' mean that function return object not equal None;
            if b'@:@' in signature:
                raise ValueError
        except AttributeError:
            raise AttributeError('Can not get access to %s function' % repr(item))

    def __init__(self,
                 img: str,
                 img_orientation='default',
                 output_format: Literal['text', 'coord', 'confidence'] | Iterable = 'text',
                 lang='en-US',
                 use_CPU=None,
                 recognition_interest: List[Tuple[float | int, float | int]] = None,
                 **args
                 ) -> None:

        self.info = output_format
        self.lang = lang
        self.use_CPU = use_CPU

        self.orientations = {
            'default': Quartz.kCGImagePropertyOrientationUp & -2,
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
                raise Exception(error.localizedDescription())
            del error

            self.all = {}
            self.output_txt = []
            self.output_crd = []
            self.output_cnf = []

            def multiply_list(values):
                """convert CGPoint to list with coordinates(x, y, width, and height)."""
                for i in range(len(values)):
                    bound_box = [round(_xy, 2) for _xy in
                                 (values[i].x, values[i].y, values.size.width, values.size.height)]
                    x, y, w, h = bound_box
                    x_1 = x * self.width
                    y_2 = (1 - y) * self.height
                    x_2 = x_1 + w * self.width
                    y_1 = y_2 - h * self.height

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
            pattern = r'[а-яА-ЯёЁ]'
            if bool(var := re.search(pattern, file)):
                raise SyntaxError(
                    f'The path to the file must\'t contain Cyrillic characters started on {var.start() + 1!r}.'
                )
            try:
                image = Vision.NSImage.alloc().initWithContentsOfFile_(
                    Cocoa.CFSTR(file)
                ).TIFFRepresentation()
                size = Vision.NSImage.alloc().initWithContentsOfFile_(Cocoa.CFSTR(img)).size()

                self.width = int(size.width)
                self.height = int(size.height)

            except AttributeError:
                raise FileNotFoundError(f'Failed to load image') from None

            cg = Cocoa.NSBitmapImageRep.imageRepWithData_(
                image
            ).CGImage()

            try:
                orient = self.orientations[img_orientation]
            except KeyError:
                raise ValueError(
                    f'Orientation must be {repr((*self.orientations.keys(), ))}'
                )

            req_handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_orientation_options_(
                cg, orient, None
            )
            self.request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(completion_handler_)
            self.request.setRevision_error_(Vision.VNRecognizeTextRequestRevision3, None)

            if recognition_interest is not None:
                try:
                    self.request.setRegionOfInterest_(
                        Cocoa.CGRect(*recognition_interest)
                    )
                except objc.internal_error:
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
                self.request.setUsesCPUOnly_(Vision.kCFBooleanTrue)

            if args:
                for (keys, values) in args.items():
                    if keys in self.request.__dir__():

                        if len(inspect.signature(eval(f'self.request.{keys}')).parameters) == 0:
                            _value = eval(
                                'self.request.%s()' % keys
                            )
                            setattr(self, keys, _value)

                        elif len(inspect.signature(eval(f'self.request.{keys}')).parameters) > 1:
                            _method = f'self.request.%s('
                            for i in range(len(values)):
                                _method += '%s, '
                            _method += ')'
                            eval(_method % (keys, *values))
                    else:
                        raise AttributeError

            with objc.autorelease_pool():
                if req_handler.isMemberOfClass_(Vision.VNImageRequestHandler):
                    req_handler.performRequests_error_([self.request], None)

        recognize(img)

    @objc.python_method
    def return_results(self) -> Dict[AnyStr, SupportsInt] | List[SupportsFloat]:
        """I created this method because when we try to return any data through a handle, we get an error.
         The Objc method cannot return or save any values."""
        if not self.all:
            try:
                return [sublist for sublist in [self.output_txt, self.output_crd, self.output_cnf] if sublist]
            except IndexError:
                return []

        else:
            return self.all

    def text_lang(self):
        return self.request.recognitionLanguages()

    def supported_languages(self):
        return self.request.supportedRecognitionLanguagesAndReturnError_(None)[0]

    def image_size(self):
        """return image width and height."""
        return [self.width, self.height]
