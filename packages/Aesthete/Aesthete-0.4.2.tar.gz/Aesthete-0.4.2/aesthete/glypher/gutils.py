proximity = 1e-3
def array_close(b1, b2) :
	for i in range(0,len(b1)) :
		if abs(b1[i]-b2[i]) >= proximity : return False
	return True
def float_close(f1, f2) :
	return abs(f1-f2) < proximity
def float_greater_than_or_equal(f1, f2) :
    return f1 >= f2-proximity
def float_greater_than(f1, f2) :
    return f1 > f2+proximity
def float_less_than(f1, f2) :
    return f1 < f2-proximity
def float_cmp(f1, f2) :
    if float_close(f1, f2) :
        return 0
    if f1 < f2 :
        return -1
    else :
        return 1

#from ElementTree website
def xml_indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            xml_indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
    return elem
