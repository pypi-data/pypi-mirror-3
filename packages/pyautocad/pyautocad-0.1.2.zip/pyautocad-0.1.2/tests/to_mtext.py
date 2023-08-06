import time
   
import autocadtools
from autocadtools import *
from object_tools import Cached

def main():
    #convert_all(get_selection())
    convert_all(None)

def get_selection():
    doc.Utility.Prompt("Select text objects")
    try:
        doc.SelectionSets.Item("SS1").Delete()
    except: 
        pass
    selection = doc.SelectionSets.Add("SS1")
    selection.SelectOnScreen()
    print selection
    return selection
    
def convert_selected():
    selection = get_selection()
    text_items = []
    text_items.extend(iter_objects("dbtext", selection))
    assert len(text_items), "no text selected"
    convert_text_to_mtext(text_items)
    doc.Regen(0)

def convert_all(container):
    for close_texts in get_close_texts(container):
        print "convert", "|".join([unformat_text(x.TextString) for x in close_texts])
    

def get_close_texts_slow(container, tolerance=2.0):
    htexts = []
    vtexts = []
    for t in iter_objects("text", container):
        #skip real multiline text
        if "dbmtext" in t.ObjectName.lower() and len(t.TextString.split("\\P")) > 1:
            continue
        if t.Rotation <> 0:
            vtexts.append(t)
        else:
            htexts.append(t)
            
    for ctexts in _get_close_texts(vtexts, tolerance, True):
        yield ctexts
    for ctexts in _get_close_texts(htexts, tolerance, False):
        yield ctexts



def get_close_texts_hand_cache(container, tolerance=2.0):
    htexts = []
    vtexts = []
    originals = dict()
    
    class Store(object):
        def __setitem__(self, key, value):
            self.__dict__[key] = value
        def __getitem__(self, key):
            return self.__dict__[key]
    begin_time = time.time()
    
    for t in iter_objects("text", container):
        #skip real multiline text
        if "dbmtext" in t.ObjectName.lower() and len(t.TextString.split("\\P")) > 1:
            continue
        
        #cache properties
        a = Store()
        a.InsertionPoint = t.InsertionPoint
        a.Rotation = t.Rotation
        a.TextString = t.TextString
        a.Height = t.Height
        #store it for later use
        originals[a] = t
        
        if a.Rotation <> 0:
            vtexts.append(a)
        else:
            htexts.append(a)
    
    print "cache objects: %.4f" % (time.time() - begin_time)                
    for ctexts in _get_close_texts(vtexts, tolerance, True):
        yield [originals[x] for x in ctexts]
    for ctexts in _get_close_texts(htexts, tolerance, False):
        yield [originals[x] for x in ctexts]

def get_close_texts(container, tolerance=2.0):
    htexts = []
    vtexts = []
    originals = dict()
    
    class Store(object):
        def __setitem__(self, key, value):
            self.__dict__[key] = value
        def __getitem__(self, key):
            return self.__dict__[key]
    begin_time = time.time()
    
    for t in iter_objects("text", container):
        #skip real multiline text
        #if "dbmtext" in t.ObjectName.lower() and len(t.TextString.split("\\P")) > 1:
        #    continue
        
        #speedup by caching (x5 times faster)
        a = Cached(t)
        
        if a.Rotation <> 0:
            vtexts.append(a)
        else:
            htexts.append(a)
    
    print "cache objects: %.4f" % (time.time() - begin_time)                
    for ctexts in _get_close_texts(vtexts, tolerance, True):
        yield [x.get_original() for x in ctexts]
    for ctexts in _get_close_texts(htexts, tolerance, False):
        yield [x.get_original() for x in ctexts]

def _get_close_texts2(texts, tolerance, is_vertical):    
    #sort by X and Y
    
    if is_vertical:
        #texts = sorted(texts, key=lambda x: (-x.InsertionPoint[1], x.InsertionPoint[0]))
        #texts = sorted(texts, key=lambda x: (x.InsertionPoint[0], x.InsertionPoint[1]))
        texts = sorted(texts, key=lambda x: (distance(x.InsertionPoint, (0.0, 0.0)), x.InsertionPoint[0]))
    else:
        texts = sorted(texts, key=lambda x: (x.InsertionPoint[0], -x.InsertionPoint[1]))
    #texts = sorted(texts, key=lambda x: x.InsertionPoint[0])

    for t in texts:
        print t.TextString

    close_texts = []
    for i in range(len(texts)-1):
        t1 = texts[i]
        t2 = texts[i + 1]

        dp = distance(t1.InsertionPoint, t2.InsertionPoint)
        if dp/t1.Height < tolerance:
            close_texts.append(t1)
        else:
            if len(close_texts):
                close_texts.append(t1)
                
                key_function = lambda x: -x.InsertionPoint[1]
                if t1.Rotation <> 0:
                    key_function = lambda x: x.InsertionPoint[0]
                
                close_texts = sorted(close_texts, key=key_function)
                yield close_texts
                close_texts = []
                
                
def _get_close_texts(texts, tolerance, is_vertical):    
    close_texts = []
    added = dict()
    num_items = len(texts)
    for i in range(num_items):
        t1 = texts[i]
        if i in added:
            continue
        for j in range(num_items):
            if i == j:
                continue
            if j in added:
                continue
                
            t2 = texts[j]

            dp = distance(t1.InsertionPoint, t2.InsertionPoint)
            # TODO: Add code to handle more than 2 strings
            if dp/t1.Height < tolerance:
                close_texts.append(t1)
                close_texts.append(t2)
                added[i] = 1
                added[j] = 1
            	key_function = lambda x: -x.InsertionPoint[1]
                if t1.Rotation <> 0:
                    key_function = lambda x: x.InsertionPoint[0]
                
                close_texts = sorted(close_texts, key=key_function)
                yield close_texts
                close_texts = []
                
   
def convert_text_to_mtext(text_items): 
    """Converts text and mtext from @text_items to one multiline text object
    """
    #sort text items by vertical Y position
    text_items = sorted(text_items, key=lambda x: -x.InsertionPoint[1])
    combined_string = "\\P".join([x.TextString for x in text_items])

    mt = doc.ActiveLayout.Block.AddMText(var(text_items[-1].InsertionPoint),
                                          max([get_text_width(x) for x in text_items]) * 1.3,
                                          combined_string)
    mt.AttachmentPoint = ACAD.acAttachmentPointBottomLeft
    mt.Height = max([x.Height for x in text_items])
    for t in text_items:
        t.Delete()
 
if __name__ == "__main__":
    begin_time = time.time()
    main()
    print "Elapsed: %.4f" % (time.time() - begin_time)