from django.conf import settings

"""The default status for pages. 1 is visible and 0 is hidden"""
CCNEWS_DEFAULT_STATUS = getattr(
            settings,
            'CCNEWS_DEFAULT_STATUS',
            1)

"""Sizes for the images in the NewsImage model"""
CCNEWS_IMAGE_SIZES = getattr(
        settings,
        'CCNEWS_IMAGE_SIZES',
        (   (140, 140),
            (240,160),
            (480,320),
            (960,640)))

"""The amount of items return for the index"""
CCNEWS_INDEX_ITEMS = getattr(
        settings,
        'CCNEWS_INDEX_ITEMS',
        10)


"""The length of the excerpt in words that will be returned from the 
excerpt filter"""
CCNEWS_EXCERPT_LENGTH = getattr(
        settings,
        'CCNEWS_EXCERPT_LENGTH',
        50)
