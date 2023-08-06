from Ft.Xml.Domlette import ValidatingReader as VR #choosen because it seems to be the only library that validate XML from a DTD

class ObjectFactory(object) :
    """Just a convenient class to recognize if an object is a factory"""
    pass

def validate_xml(xml_file) :
    
    """Just verify if the xml file is valid. If the function does not raise an error the file is valid.
    TODO : Find a way to validate the file with gnosis.xml directly.
    """
    VR.parseUri(xml_file)
    return True