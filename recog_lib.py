import Vision
import Cocoa


class Recognition:
    def get_info_from_image(self, img, output_format):
        self.info = output_format

        def handle(request, error):
            self.all = {}
            self.output_txt = []
            self.output_crd = []
            
            for result in request.results():
                if isinstance(result, Vision.VNRecognizedTextObservation):
                    for texts in result.topCandidates_(1):
                        
                        if self.info == 'text':
                            self.output_txt.append(texts.string())
                            
                        elif self.info == 'coord':
                            self.output_crd.append(result.boundingBox())
                            
                        elif self.info == 'coord+text' or self.info == 'text+coord':
                            self.output_txt.append(texts.string())
                            self.output_crd.append(result.boundingBox())
                            self.all.update(
                                {
                                        'coord': self.output_crd,
                                        'text': self.output_txt
                                }
                            )
                        else:
                            pass #???

        def recognize(img):
            try:
                image = Vision.NSImage.alloc().initWithContentsOfFile_(img).TIFFRepresentation()
            except AttributeError:
                raise FileNotFoundError('Failed to load image..')

            cg = Cocoa.NSBitmapImageRep.imageRepWithData_(image).CGImage()
            req_handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(cg, None)
            
            request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handle)
            request.setRevision_(Vision.VNRecognizeTextRequestRevision3)
            request.setUsesLanguageCorrection_(False)
            req_handler.performRequests_error_([request], None)
        recognize(img)

    def return_results(self):
        """Call this method because when we try return any data through handle we get an error."""
        if self.all is {}: 
            return self.output_txt or self.output_crd
        return self.all






