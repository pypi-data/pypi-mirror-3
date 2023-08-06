import pmedian

def pyomo_preprocess(**kwds):
    print "PREPROCESSING",kwds.keys()

def pyomo_create_model(**kwds):
    print "CREATING MODEL",kwds.keys()
    return pmedian.model

def pyomo_print_model(**kwds):
    print "PRINTING MODEL",kwds.keys()

def pyomo_print_instance(**kwds):
    print "PRINTING INSTANCE",kwds.keys()

def pyomo_save_instance(**kwds):
    print "SAVE INSTANCE",kwds.keys()

def pyomo_print_results(**kwds):
    print "PRINTING RESULTS",kwds.keys()

def pyomo_save_results(**kwds):
    print "SAVING RESULTS",kwds.keys()

def pyomo_postprocess(**kwds):
    print "POSTPROCESSING",kwds.keys()
