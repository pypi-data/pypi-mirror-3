from Products.CMFPlone.utils import getToolByName
from Products.Five import BrowserView
from plone.memoize.instance import memoize

MAX_TAGS = 50

class TagCloud(BrowserView):

    def calcTagSize(self, number, min_d, max_d):
        min,max = 100,300
        rc = float(max-min)
        rc *= float(number-min_d)
        rc /= float(max_d-min_d)
        rc += float(min)
        return int(rc)

    @memoize
    def subjects(self):
        pc = getToolByName(self.context, 'portal_catalog')
        total = 0
        d = {}
        for result in pc():
            for subject in result.Subject or []:
                if subject not in d: d[subject] = 0
                d[subject] += 1
                total += 1
        d_val = d.values()
        if d_val:
            d_val.sort()
            if len(d_val) > MAX_TAGS:
                min_d = d_val[-MAX_TAGS]
            else:
                min_d = d_val[0]
            max_d = d_val[-1] 
        else:
            min_d = max_d = 0
        d_keys = [ x for x in d.keys() if d[x] >= min_d ]
        d_keys.sort()
        l = [ (x, self.calcTagSize(d[x], min_d, max_d),
                   'search?Subject%3Alist=' + x ) for x in d_keys ]
        return l[:MAX_TAGS]

