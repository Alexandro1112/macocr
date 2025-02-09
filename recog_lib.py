import Vision
import Cocoa
import re
from typing import Dict, SupportsFloat, SupportsInt, List, AnyStr, Tuple, Any
import objc
from collections.abc import Iterable


class Recognition:
    """
    Class create Recognition object
    and accept:

    :argument img: path to require image, can not contain Cyrillic characters.

    :argument output_format: explanation of what we need to return, text if we need text from image. coord,
    if a need get a coordinates of text, confidence if we need get accurate of recognized text in float values.

    :argument lang: language of recognition text, if text contain more 2 languages keep lang at ``en-US``.

    :argument use_CPU: This method (or property) allows you to specify that text recognition should be performed only on
     the central processing unit (CPU) rather than on the graphics processing unit (GPU). This can be useful in
     certain scenarios, for example, when it is important to reduce the load on the device's hardware resources.

    :argument recognition_interest: argument accept dict with coordinates, this is need for a limit text recognition by
    x, y, width and height coordinates.

    """
    def __init__(self,
                 img: str,
                 output_format='text',
                 lang='en-US',
                 use_CPU=None,
                 recognition_interest: List[Tuple[float | int, float | int]] = None
                 ) -> None:
        self.info = output_format
        self.lang = lang
        self.use_CPU = use_CPU

        def completion_handler_(request, error):
            """
            Create handler for accept recognized text and errors.
            """
            if error is None: del error
            self.all = {}
            self.output_txt = []
            self.output_crd = []
            self.output_cnf = []

            def multiply_list(values):
                """convert CGPoint to list with coordinates(x, y, width, and height)."""
                for i in range(len(values)):
                    return [values[i].x, values[i].y, values.size.width, values.size.height]

            if not isinstance(request.results(), Iterable) and recognition_interest is not None:
                self.output_txt.append([]) # If we limit text recognition by coordinates, and if nothing is found at the
                # given coordinates, then we return an empty dictionary.
                return

            for result in request.results():
                if isinstance(result, Vision.VNRecognizedTextObservation):
                    for text in result.topCandidates_(1):

                        if self.info == 'text':
                            self.output_txt.append(text.string())
                            self.all = {}

                        elif self.info == 'coord':
                            self.output_crd.append(multiply_list(result.boundingBox()))
                            self.all = {}

                        elif self.info == 'confidence':
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
                            pass

        def recognize(img: Vision.CFSTR) -> None:
            pattern = r'[а-яА-ЯёЁ]'
            if bool(var := re.search(pattern, img)):
                raise SyntaxError(
                    f'The path to the file must\'t contain Cyrillic characters started on {var.start() + 1!r}.'
                )

            if 'file:' in img:
                img = img.replace('file:', '')

            try:
                image = Vision.NSImage.alloc().initWithContentsOfFile_(
                    Vision.CFSTR(img)
                ).TIFFRepresentation()

            except AttributeError:
                raise FileNotFoundError('Failed to load image.') from None

            cg = Cocoa.NSBitmapImageRep.imageRepWithData_(
                image
            ).CGImage()

            req_handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(
                cg, None
            )
            self.request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(completion_handler_)
            self.request.setRevision_(Vision.VNRecognizeTextRequestRevision3)

            if recognition_interest is not None:
                self.request.setRegionOfInterest_(
                    Cocoa.CGRect(recognition_interest[0])
                )
            elif recognition_interest is None:
                pass
            else:
                raise ValueError(
                    'Recognition interest has wrong type or values.'
                )

            if not self.lang == 'en-US':
                self.request.setRecognitionLanguages_(lang)
            if self.use_CPU is not None:
                self.request.setUsesCPUOnly_(True)

            req_handler.performRequests_error_([self.request], None)

        recognize(img)
        
    @objc.python_method
    def return_results(self) -> Dict[AnyStr, SupportsInt] | List[SupportsFloat]:
        """I created this method because when we try to return any data through a handle, we get an error.
         The Objc method cannot keep or return any values."""
        if self.all == {}:
            return self.output_txt or self.output_crd or self.output_cnf
        else:
            return self.all

    def text_lang(self):
        return self.request.recognitionLanguages()
