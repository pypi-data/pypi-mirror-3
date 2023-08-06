import sys
from xml.dom.minidom import Document


def appendXML(doc, usage_list, cac_dict, period):

    # Create the main <usage_from> element
    usage = doc.createElement("usage")
    usage.setAttribute("from", period)
    usage.setAttribute("site", "pdc")
    usage.setAttribute("to", period)
    usage_list.appendChild(usage)
    
    # Create a <proposal_id> element
    for cac in cac_dict.keys():
        the_handle = cac_dict[cac]
        temp = list(cac)
        temp[3] = "/"
        formatted_cac = "".join(temp)
        proposal = doc.createElement("proposal")
        #proposal.setAttribute("id", "SNIC 000/00-00")
        proposal.setAttribute("id", "SNIC "+formatted_cac)
        usage.appendChild(proposal)
        
        resource = doc.createElement("resource")
        resource.setAttribute("id", "cray_xe6")
        proposal.appendChild(resource)
        
        time = doc.createElement("time")
        resource.appendChild(time)
        timex = doc.createTextNode(str(round(the_handle.getUsedCoreHours())))
        
        time.appendChild(timex)
    return doc


def time_to_hours(time_str):
    try:
        hours, minutes, seconds = time_str.split(':')
    except ValueError:
        return -1
    return int(hours) + int(minutes)/60.0 + int(seconds)/3600.0

