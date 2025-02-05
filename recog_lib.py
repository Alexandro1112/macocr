import Vision


class Recognition:
    def get_info_from_image(self, img, output_format):
        self.info = output_format

        def handle(request, error):
            self.output = []
            for result in request.results():
                if isinstance(result, Vision.VNRecognizedTextObservation):
                    for texts in result.topCandidates_(1):
                        if self.info == 'text':
                            self.output.append(texts.string())
                        if self.info == 'coord':
                            abst_position = result.boundingBox()
                            self.output.append(abst_position)
                        else:
                            return None

        def recognize(img):
            image = Vision.NSImage.alloc().initWithContentsOfFile_(img)
            if image is None:
                raise FileNotFoundError('Failed to load image..')
            rep = image.representations()[0]
            cg_image = rep.CGImage()
            req_handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(cg_image, None)
            request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handle)
            req_handler.performRequests_error_([request], None)
        recognize(img)

    def return_results(self):
        return self.output
