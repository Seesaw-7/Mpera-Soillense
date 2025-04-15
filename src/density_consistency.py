import re


def get_density(uscs, sptn):
    if type(uscs) != str: 
        return None
    types = re.findall(r'\b[A-Z]{2}\b', uscs)
    coarse, fine= False, False
    for t in types:
        if t in ["GW", "GP", "GM", "GC", "SW", "SP", "SM", "SC"]:
            coarse = True
            break
        elif t in ["ML", "CL", "OL", "MH", "CH", "OH", "PT"]:
            fine = True
    
    if coarse:
        if sptn <= 4:
            return 'Very loose'
        elif sptn <= 10:
            return 'Loose'
        elif sptn <= 24:
            return 'Medium Dense'
        elif sptn <= 50:
            return 'Dense'
        else:
            return 'Very Dense'
    elif fine:
        if sptn <= 2:
            return 'Very soft'
        elif sptn <= 4:
            return 'Soft'
        elif sptn <= 8:
            return 'Medium Stiff'
        elif sptn <= 15:
            return 'Stiff'
        elif sptn <= 30:
            return 'Very stiff'
        else:
            return 'Hard'
