import Vision
import Cocoa
import re


class Recognition:
    """
    Class create Recognition object
    and accept
    :argument img: path to require image
    :argument output_format: explanation of what we need to return
    """
    def __init__(self, img, output_format):
        self.info = output_format

        def handle(request, error):
            self.all = {}
            self.output_txt = []
            self.output_crd = []
            for result in request.results():
                if isinstance(result, Vision.VNRecognizedTextObservation):
                    for text in result.topCandidates_(1):
                        if self.info == 'text':
                            self.output_txt.append(text.string())
                            self.all = {}

                        if self.info == 'coord':
                            self.output_crd.append(result.boundingBox())
                            self.all = {}

                        elif self.info == 'coord+text' or self.info == 'text+coord':
                            self.output_txt.append(text.string())
                            self.output_crd.append(result.boundingBox())
                            self.all.update({
                                    'coord': self.output_crd,
                                    'text': self.output_txt
                            })
                        else:
                            return None
            del error

        def recognize(img: Vision.CFSTR) -> None:
            pattern = r'[а-яА-ЯёЁ]'
            if bool(var := re.search(pattern, img)):
                raise SyntaxError(
                    f'The path to the file must not contain Cyrillic characters on {var.span()!r} pos.'
                )
            try:
                image = Vision.NSImage.alloc().initWithContentsOfFile_(
                    Vision.CFSTR(img.replace('file:', ''))
                ).TIFFRepresentation()

            except AttributeError:
                raise FileNotFoundError('Failed to load image.') from None

            cg = Cocoa.NSBitmapImageRep.imageRepWithData_(
                image
            ).CGImage()

            req_handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(
                cg, None
            )
            request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handle)

            request.setRevision_(Vision.VNRecognizeTextRequestRevision3)
            req_handler.performRequests_error_([request], None)

        recognize(img)

    def return_results(self):
        """I created this method because when we try to return any data through a handle, we get an error.
         The Objc method cannot keep or return any text. """
        if self.all == {}:
            return self.output_txt or self.output_crd
        else:
            return self.all






