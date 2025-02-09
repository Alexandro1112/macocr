from .recog_lib import Recognition
from langcodes import Language
import CoreAudio


def supported_langs():
    """
    get all ISO Languages codes and convert it from ISO 639 to full name.
    :return:
    """
    _list = []
    for lang in CoreAudio.CFLocaleCopyISOLanguageCodes():
        _list.append(Language(lang).language_name())
    return _list


__all__ = [Recognition, supported_langs]

