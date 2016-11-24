def visParamsBuilder(Min, Max, bands):
    """  """
    visParams = {}
    if Min and Max and Min < Max:
        visParams['min'] = Min
        visParams['max'] = Max
    visParams['bands'] = bands
    return visParams

def imageToMapId(image, visParams):
    """  """
    mapId = image.getMapId(visParams)
    values = {
        'mapid': mapId['mapid'],
        'token': mapId['token']
    }
    return values