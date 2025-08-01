from django import template

from django.urls import reverse

register = template.Library()



@register.filter
def multiply(value, arg):
    """Multiplies the given value by the argument."""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0  # Return 0 if there's an issue




@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)




@register.filter
def pluck(queryset, field_name):
    """
    Extracts a list of values for a given field from a queryset.
    """
    return [getattr(obj, field_name) for obj in queryset]

@register.filter
def intersect(list1, list2):
    """
    Returns the intersection of two lists.
    """
    return list(set(list1) & set(list2))


@register.filter
def dict_lookup(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None  # Return None if the input is not a dictionary



@register.filter
def get_modality_url_name(modality):
    """
    Returns the URL name corresponding to a specific modality.
    """
    url_map = {
        "Ultrasound": "zonal_offices:ultrasound_score",
        "Conventional X-ray": "zonal_offices:xray_score",
        "CT Scan": "zonal_offices:ctscan_score",
        "MRI": "zonal_offices:mri_score",
        "Radiotherapy": "zonal_offices:radiotherapy_score",
        "Nuclear Medicine": "zonal_offices:nuclear_medicine_score",
        "Mammography": "zonal_offices:mammography_score",
        "Dental X-ray": "zonal_offices:dental_xray_score",
        "Echocardiography": "zonal_offices:echocardiography_score",
        "Angiography": "zonal_offices:angiography_score",
        "C-Arm/O-ARM": "zonal_offices:carm_score",
    }
    return url_map.get(modality, None)


@register.filter
def get_modality_update_url_name(modality):
    """
    Returns the URL name corresponding to a specific modality.
    """
    url_map = {
        "Ultrasound": "zonal_offices:ultrasound_update",
        "Conventional X-ray": "zonal_offices:xray_update",
        "CT Scan": "zonal_offices:ctscan_update",
        "MRI": "zonal_offices:mri_update",
        "Radiotherapy": "zonal_offices:radiotherapy_update",
        "Nuclear Medicine": "zonal_offices:nuclear_medicine_update",
        "Mammography": "zonal_offices:mammography_update",
        "Dental X-ray": "zonal_offices:dental_xray_update",
        "Echocardiography": "zonal_offices:echocardiography_update",
        "Angiography": "zonal_offices:angiography_update",
        "C-Arm/O-ARM": "zonal_offices:carm_update",
    }
    return url_map.get(modality, None)


@register.filter
def get_status_message(object):
    status_messages = {
        ("Hospital", 1): "Start Registration",
        ("Document", 1): "Make Payment",
        ("Payment", 2): "Payment Verification",
        ("Payment", 3): "Verifications Completed",
        ("Schedule", 4): "Inspection Scheduled",
        ("Inspection", 5): "Facility Inspection",
        ("Inspection", 6): "Inspection Approved",
        ("Inspection", 7): "Final Approval",
        ("Internship", 5): "Facility Inspection",
        ("Internship", 6): "Inspection Approved",
        ("Internship", 7): "Final Approval",
        ("License", 8): "Complete",
    }
    return status_messages.get(
        (object.model_name, object.application_status), "Unknown"
    )



@register.filter
def get_monitoring_status_message(object):
    status_messages = {
        ("Hospital", 1): "Start Registration",
        ("Document", 1): "Payment Processing",
        ("Payment", 2): "Payment Verification",
        ("Payment", 3): "Payment Verified",
        ("Schedule", 4): "Inspection Scheduled",
        ("Inspection", 5): "Facility Inspection",
        ("Inspection", 6): "Inspection Approved",
        ("Inspection", 7): "Final Approval",
        ("Internship", 5): "Facility Inspection",
        ("Internship", 6): "Inspection Approved",
        ("Internship", 7): "Final Approval",
        ("License", 8): "Complete",
    }
    return status_messages.get(
        (object.model_name, object.application_status), "Unknown"
    )


@register.filter
def get_action_url(object):
    # Define the mapping for URLs based on attributes
    action_mapping = {
        # Document mappings
        ("Document", "New Registration - Radiography Practice Permit", 1): 
            lambda app: reverse("hospitals:generate_invoice", args=[app.pk]),    
        ("Document", "New Registration - Government Hospital Internship", 1): 
            lambda app: reverse("hospitals:generate_accreditation_payment_details", args=[app.pk]),
        ("Document", "New Registration - Private Hospital Internship", 1): 
            lambda app: reverse("hospitals:generate_accreditation_invoice", args=[app.pk]),
        ("Document", "Renewal - Radiography Practice Permit", 1): 
            lambda app: reverse("hospitals:generate_renewal_invoice", args=[app.pk]), 
        ("Document", "Renewal - Private Hospital Internship", 1): 
            lambda app: reverse("hospitals:generate_accreditation_invoice", args=[app.pk]),
        ("Document", "Renewal - Government Hospital Internship", 1): 
            lambda app: reverse("hospitals:generate_accreditation_payment_details", args=[app.pk]),


        # Payment mappings
        ("Payment", "New Registration - Radiography Practice Permit", 2): 
            lambda app: reverse("hospitals:payment_verifications", args=[app.pk]),
        ("Payment", "New Registration - Government Hospital Internship", 2): 
            lambda app: reverse("hospitals:accreditation_payment_verifications", args=[app.pk]),
        ("Payment", "New Registration - Private Hospital Internship", 2): 
            lambda app: reverse("hospitals:accreditation_payment_verifications", args=[app.pk]),
        ("Payment", "Renewal - Radiography Practice Permit", 2): 
            lambda app: reverse("hospitals:payment_verifications", args=[app.pk]),
        ("Payment", "Renewal - Private Hospital Internship", 2): 
            lambda app: reverse("hospitals:accreditation_payment_verifications", args=[app.pk]),
        ("Payment", "Renewal - Government Hospital Internship", 2): 
            lambda app: reverse("hospitals:accreditation_payment_verifications", args=[app.pk]),
        

        ("Payment", "New Registration - Radiography Practice Permit", 3): 
            lambda app: reverse("hospitals:verifications_completed", args=[app.id]),
        ("Payment", "New Registration - Government Hospital Internship", 3): 
            lambda app: reverse("hospitals:accreditation_verifications_completed", args=[app.id]),
        ("Payment", "New Registration - Private Hospital Internship", 3): 
            lambda app: reverse("hospitals:accreditation_verifications_completed", args=[app.id]),
        ("Payment", "Renewal - Radiography Practice Permit", 3): 
            lambda app: reverse("hospitals:verifications_completed", args=[app.id]),
        ("Payment", "Renewal - Private Hospital Internship", 3): 
            lambda app: reverse("hospitals:accreditation_verifications_completed", args=[app.id]),
        ("Payment", "Renewal - Government Hospital Internship", 3): 
            lambda app: reverse("hospitals:accreditation_verifications_completed", args=[app.id]),
        ("Payment", "Renewal - Radiography Practice Permit", 7): 
            lambda app: reverse("hospitals:practice_permit_renewal_final_approval", args=[app.pk]),


        # Schedule mappings
        ("Schedule", "New Registration - Radiography Practice Permit", 4): 
            lambda app: reverse("hospitals:inspection_processing", args=[app.id]),
        ("Schedule", "New Registration - Government Hospital Internship", 4): 
            lambda app: reverse("hospitals:schedule_detail", args=[app.id]),
        ("Schedule", "New Registration - Private Hospital Internship", 4): 
            lambda app: reverse("hospitals:schedule_detail", args=[app.id]),
        ("Schedule", "Renewal - Private Hospital Internship", 4): 
            lambda app: reverse("hospitals:schedule_detail", args=[app.id]),
        ("Schedule", "Renewal - Government Hospital Internship", 4): 
            lambda app: reverse("hospitals:schedule_detail", args=[app.id]),

       
        # Inspection mappings
        ("Inspection", "New Registration - Radiography Practice Permit", 5): 
            lambda app: reverse("hospitals:inspection_processing", args=[app.id]),
        ("Inspection", "Renewal - Radiography Practice Permit", 5): 
            lambda app: reverse("hospitals:inspection_processing", args=[app.id]),
        ("Inspection", "New Registration - Radiography Practice Permit", 6): 
            lambda app: reverse("hospitals:inspection_passed", args=[app.pk]),
        ("Inspection", "New Registration - Radiography Practice Permit", 7): 
            lambda app: reverse("hospitals:license_issuance", args=[app.pk]),

        # Internship mappings
        ("Internship", "New Registration - Government Hospital Internship", 5): 
            lambda app: reverse("hospitals:appraisal_processing", args=[app.pk]),
        ("Internship", "New Registration - Private Hospital Internship", 5): 
            lambda app: reverse("hospitals:appraisal_processing", args=[app.pk]),
        ("Internship", "Renewal - Private Hospital Internship", 5): 
            lambda app: reverse("hospitals:appraisal_processing", args=[app.pk]),
        ("Internship", "Renewal - Government Hospital Internship", 5): 
            lambda app: reverse("hospitals:appraisal_processing", args=[app.pk]),
            
        ("Internship", "New Registration - Government Hospital Internship", 6): 
            lambda app: reverse("hospitals:appraisal_passed", args=[app.id]),
        ("Internship", "New Registration - Private Hospital Internship", 6): 
            lambda app: reverse("hospitals:appraisal_passed", args=[app.id]),
        ("Internship", "Renewal - Private Hospital Internship", 6): 
            lambda app: reverse("hospitals:appraisal_passed", args=[app.id]),
        ("Internship", "Renewal - Government Hospital Internship", 6): 
            lambda app: reverse("hospitals:hospitals:appraisal_passed", args=[app.id]),

        ("Internship", "New Registration - Government Hospital Internship", 7): 
            lambda app: reverse("hospitals:internship_license_issuance", args=[app.pk]),
        ("Internship", "New Registration - Private Hospital Internship", 7): 
            lambda app: reverse("hospitals:internship_license_issuance", args=[app.pk]),
        ("Internship", "Renewal - Private Hospital Internship", 7): 
            lambda app: reverse("hospitals:internship_license_issuance", args=[app.pk]),
        ("Internship", "Renewal - Government Hospital Internship", 7): 
            lambda app: reverse("hospitals:internship_license_issuance", args=[app.pk]),

        # License mappings
        ("License", "New Registration - Radiography Practice Permit", 8): 
            lambda app: reverse("hospitals:license_details", args=[app.id]),
        ("License", "New Registration - Government Hospital Internship", 8): 
            lambda app: reverse("hospitals:license_details", args=[app.pk]),
        ("License", "New Registration - Private Hospital Internship", 8): 
            lambda app: reverse("hospitals:license_details", args=[app.pk]),
        ("License", "Renewal - Radiography Practice Permit", 8): 
            lambda app: reverse("hospitals:license_details", args=[app.id]),
        ("License", "Renewal - Private Hospital Internship", 8): 
            lambda app: reverse("hospitals:license_details", args=[app.pk]),
        ("License", "Renewal - Government Hospital Internship", 8): 
            lambda app: reverse("hospitals:license_details", args=[app.pk]),
    }
    
    # Check if object has required attributes
    if hasattr(object, 'model_name'):
        # For "Document" module, use object.application_type
        if object.model_name == "Document":
            application_type = object.application_type
        # elif hasattr(object, 'hospital') and hasattr(object.hospital, 'application_type'):
            # For other modules, use object.hospital.application_type
            # application_type = object.hospital.application_type
        else:
            application_type = object.hospital.application_type
            # return None  # If no application type found, return None

        # Create the key based on model_name, application_type, and optionally application_status
        key = (object.model_name, application_type)
        
        # Add application_status to the key if it exists
        if hasattr(object, 'application_status'):
            key = (object.model_name, application_type, object.application_status)
        
        # Get the corresponding action function from the mapping
        action_function = action_mapping.get(key)
        
        # Return the generated URL or None if no match
        return action_function(object) if action_function else None
    
    return None





@register.filter
def get_monitoring_action_url(object):
    # Define the mapping for URLs based on attributes
    action_mapping = {
        # Document mappings

        # ("Hospital", "Radiography Practice Permit", 1): 
        #     lambda app: reverse("monitoring:hospital_profile_details", args=[app.pk]),    
        # ("Hospital", "Gov Internship Accreditation", 1): 
        #     lambda app: reverse("monitoring:hospital_profile_details", args=[app.pk]),
        # ("Hospital", "Pri Internship Accreditation", 1): 
        #     lambda app: reverse("monitoring:hospital_profile_details", args=[app.pk]),
        # ("Hospital", "Radiography Practice Permit Renewal", 1): 
        #     lambda app: reverse("monitoring:hospital_profile_details", args=[app.pk]), 
        # ("Hospital", "Pri Internship Accreditation Renewal", 1): 
        #     lambda app: reverse("monitoring:hospital_profile_details", args=[app.pk]),
        # ("Hospital", "Gov Internship Accreditation Renewal", 1): 
        #     lambda app: reverse("monitoring:hospital_profile_details", args=[app.pk]),



        ("Document", "New Registration - Radiography Practice Permit", 1): 
            lambda app: reverse("monitoring:hospital_registration_details", args=[app.pk]),    
        ("Document", "New Registration - Government Hospital Internship", 1): 
            lambda app: reverse("monitoring:hospital_registration_details", args=[app.pk]),
        ("Document", "New Registration - Private Hospital Internship", 1): 
            lambda app: reverse("monitoring:hospital_registration_details", args=[app.pk]),
        ("Document", "Renewal - Radiography Practice Permit", 1): 
            lambda app: reverse("monitoring:hospital_registration_details", args=[app.pk]), 
        ("Document", "Renewal - Private Hospital Internship", 1): 
            lambda app: reverse("monitoring:hospital_registration_details", args=[app.pk]),
        ("Document", "Renewal - Government Hospital Internship", 1): 
            lambda app: reverse("monitoring:hospital_registration_details", args=[app.pk]),


        # Payment mappings
        ("Payment", "New Registration - Radiography Practice Permit", 2): 
            lambda app: reverse("monitoring:hospital_payment_details", args=[app.pk]),
        ("Payment", "New Registration - Government Hospital Internship", 2): 
            lambda app: reverse("monitoring:hospital_payment_details", args=[app.pk]),
        ("Payment", "New Registration - Private Hospital Internship", 2): 
            lambda app: reverse("monitoring:hospital_payment_details", args=[app.pk]),
        ("Payment", "Renewal - Private Hospital Internship", 2): 
            lambda app: reverse("monitoring:hospital_payment_details", args=[app.pk]),
        ("Payment", "Renewal - Government Hospital Internship", 2): 
            lambda app: reverse("monitoring:hospital_payment_details", args=[app.pk]),
        
        ("Payment", "Renewal - Radiography Practice Permit", 2): 
            lambda app: reverse("monitoring:hospital_payment_details", args=[app.pk]),

        ("Payment", "New Registration - Radiography Practice Permit", 3): 
            lambda app: reverse("monitoring:hospital_verification_details", args=[app.id]),
        ("Payment", "New Registration - Government Hospital Internship", 3): 
            lambda app: reverse("monitoring:hospital_verification_details", args=[app.id]),
        ("Payment", "New Registration - Private Hospital Internship", 3): 
            lambda app: reverse("monitoring:hospital_verification_details", args=[app.id]),
        ("Payment", "Renewal - Radiography Practice Permit", 3): 
            lambda app: reverse("monitoring:hospital_verification_details", args=[app.id]),
        ("Payment", "Renewal - Private Hospital Internship", 3): 
            lambda app: reverse("monitoring:hospital_verification_details", args=[app.id]),
        ("Payment", "Renewal - Government Hospital Internship", 3): 
            lambda app: reverse("monitoring:hospital_verification_details", args=[app.id]),
        ("Payment", "Renewal - Radiography Practice Permit", 3): 
            lambda app: reverse("monitoring:hospital_inspection_registrar_approval_details", args=[app.pk]),


        # Schedule mappings
        ("Schedule", "New Registration - Radiography Practice Permit", 4): 
            lambda app: reverse("monitoring:hospital_schedule_details", args=[app.id]),
        ("Schedule", "New Registration - Government Hospital Internship", 4): 
            lambda app: reverse("monitoring:hospital_schedule_details", args=[app.id]),
        ("Schedule", "New Registration - Private Hospital Internship", 4): 
            lambda app: reverse("monitoring:hospital_schedule_details", args=[app.id]),
        ("Schedule", "Renewal - Private Hospital Internship", 4): 
            lambda app: reverse("monitoring:hospital_schedule_details", args=[app.id]),
        ("Schedule", "Renewal - Government Hospital Internship", 4): 
            lambda app: reverse("monitoring:hospital_schedule_details", args=[app.id]),

       
        # Inspection mappings
        ("Inspection", "New Registration - Radiography Practice Permit", 5): 
            lambda app: reverse("monitoring:hospital_inspection_details", args=[app.id]),
        ("Inspection", "Renewal - Radiography Practice Permit", 5): 
            lambda app: reverse("monitoring:hospital_inspection_details", args=[app.id]),
        ("Inspection", "New Registration - Radiography Practice Permit", 6): 
            lambda app: reverse("monitoring:hospital_inspection_approval_details", args=[app.pk]),
        ("Inspection", "New Registration - Radiography Practice Permit", 7): 
            lambda app: reverse("monitoring:hospital_inspection_registrar_approval_details", args=[app.pk]),

        # Internship mappings
        ("Internship", "New Registration - Government Hospital Internship", 5): 
            lambda app: reverse("monitoring:hospital_accreditation_details", args=[app.pk]),
        ("Internship", "New Registration - Private Hospital Internship", 5): 
            lambda app: reverse("monitoring:hospital_accreditation_details", args=[app.pk]),
        ("Internship", "Renewal - Private Hospital Internship", 5): 
            lambda app: reverse("monitoring:hospital_accreditation_details", args=[app.pk]),
        ("Internship", "Renewal - Government Hospital Internship", 5): 
            lambda app: reverse("monitoring:hospital_accreditation_details", args=[app.pk]),
            
        ("Internship", "New Registration - Government Hospital Internship", 6): 
            lambda app: reverse("monitoring:hospital_accreditation_approval_details", args=[app.pk]),
        ("Internship", "New Registration - Private Hospital Internship", 6): 
            lambda app: reverse("monitoring:hospital_accreditation_approval_details", args=[app.pk]),
        ("Internship", "Renewal - Private Hospital Internship", 6): 
            lambda app: reverse("monitoring:hospital_accreditation_approval_details", args=[app.pk]),
        ("Internship", "Renewal - Government Hospital Internship", 6): 
            lambda app: reverse("monitoring:hospital_accreditation_approval_details", args=[app.pk]),

        ("Internship", "New Registration - Government Hospital Internship", 7): 
            lambda app: reverse("monitoring:hospital_accreditation_registrar_approval_details", args=[app.pk]),
        ("Internship", "New Registration - Private Hospital Internship", 7): 
            lambda app: reverse("monitoring:hospital_accreditation_registrar_approval_details", args=[app.pk]),
        ("Internship", "Renewal - Private Hospital Internship", 7): 
            lambda app: reverse("monitoring:hospital_accreditation_registrar_approval_details", args=[app.pk]),
        ("Internship", "Renewal - Government Hospital Internship", 7): 
            lambda app: reverse("monitoring:hospital_accreditation_registrar_approval_details", args=[app.pk]),

        # License mappings
        ("License", "New Registration - Radiography Practice Permit", 8): 
            lambda app: reverse("monitoring:hospital_license_details", args=[app.pk]),
        ("License", "New Registration - Government Hospital Internship", 8): 
            lambda app: reverse("monitoring:hospital_license_details", args=[app.pk]),
        ("License", "New Registration - Private Hospital Internship", 8): 
            lambda app: reverse("monitoring:hospital_license_details", args=[app.pk]),
        ("License", "Renewal - Radiography Practice Permit", 8): 
            lambda app: reverse("monitoring:hospital_license_details", args=[app.pk]),
        ("License", "Renewal - Private Hospital Internship", 8): 
            lambda app: reverse("monitoring:hospital_license_details", args=[app.pk]),
        ("License", "Renewal - Government Hospital Internship", 8): 
            lambda app: reverse("monitoring:hospital_license_details", args=[app.pk]),
    }
    
    # Check if object has required attributes
    if hasattr(object, 'model_name'):
        # For "Document" module, use object.application_type
        if object.model_name == "Document":
            application_type = object.application_type

        elif object.model_name == "Hospital":
            application_type = object.type
        elif object.model_name == "Appraisal":
            application_type = object.hospital.application_type
        # elif hasattr(object, 'hospital') and hasattr(object.hospital, 'application_type'):
            # For other modules, use object.hospital.application_type
            # application_type = object.hospital.application_type
        else:
            application_type = object.hospital.application_type
            # return None  # If no application type found, return None

        # Create the key based on model_name, application_type, and optionally application_status
        key = (object.model_name, application_type)
        
        # Add application_status to the key if it exists
        if hasattr(object, 'application_status'):
            key = (object.model_name, application_type, object.application_status)
        
        # Get the corresponding action function from the mapping
        action_function = action_mapping.get(key)
        
        # Return the generated URL or None if no match
        return action_function(object) if action_function else None
    
    return None


@register.simple_tag
def get_hospital_action_url(object):
    """Generates the appropriate action URL for the given hospital."""
    url_mapping = {
        "Radiography Practice Permit": "hospitals:start_new_radiography_license_application",
        "Gov Internship Accreditation": "hospitals:start_gov_internship_accreditation_application",
        "Pri Internship Accreditation": "hospitals:start_pri_internship_accreditation_application",
        "Radiography Practice Permit Renewal": "hospitals:start_new_practice_permit_renewal",
        "Pri Internship Accreditation Renewal": "hospitals:start_new_pri_internship_renewal",
        "Gov Internship Accreditation Renewal": "hospitals:start_new_gov_internship_renewal",
    }
    
    url_name = url_mapping.get(object.type)
    if url_name:
        return reverse(url_name, args=[object.pk])
    return None




@register.simple_tag
def get_monitoring_hospital_action_url(object):
    """Generates the appropriate action URL for the given hospital."""
    url_mapping = {
        "Radiography Practice Permit": "monitoring:hospital_profile_details",
        "Gov Internship Accreditation": "monitoring:hospital_profile_details",
        "Pri Internship Accreditation": "monitoring:hospital_profile_details",
        "Radiography Practice Permit Renewal": "monitoring:hospital_profile_details",
        "Pri Internship Accreditation Renewal": "monitoring:hospital_profile_details",
        "Gov Internship Accreditation Renewal": "monitoring:hospital_profile_details",
    }
    
    url_name = url_mapping.get(object.type)
    if url_name:
        return reverse(url_name, args=[object.pk])
    return None


# @register.filter
# def instanceof(obj, class_name):
#     return obj.__class__.__name__.lower() == class_name.lower()



@register.filter
def instanceof(obj, class_name):
    """Custom template filter to check if an object is an instance of a given class."""
    return obj.__class__.__name__ == class_name




# @register.filter
# def get_status_message(object):
#     # Check if `application` is a dict-like object or has required attributes
#     if hasattr(object, "model_name") and hasattr(object, "application_status"):
#         key = (object.model_name, object.application_status)
#     elif isinstance(object, dict):
#         key = (object.get("model_name"), object.get("application_status"))
#     else:
#         return "Invalid Application Object"

#     # Define status messages
#     status_messages = {
#         ("Document", None): "Payment Processing",
#         ("Payment", 1): "Payment Verification",
#         ("Payment", 3): "Payment Verified",
#         ("Schedule", None): "Inspection Scheduled",
#         ("Inspection", 5): "Facility Inspection",
#         ("Inspection", 6): "Inspection Approved",
#         ("Inspection", 7): "Final Approval",
#         ("Internship", 5): "Facility Inspection",
#         ("Internship", 6): "Inspection Approved",
#         ("Internship", 7): "Final Approval",
#         ("License", None): "Complete",
#     }
    
#     return status_messages.get(key, "Unknown")
