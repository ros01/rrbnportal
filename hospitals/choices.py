STATE_CHOICES = (
        ('Abia', 'Abia' ),
        ('Adamawa', 'Adamawa'),
        ('Akwa Ibom', 'Akwa Ibom'),
        ('Anambra', 'Anambra'),
        ('Bauchi', 'Bauchi'),
        ('Bayelsa', 'Bayelsa'),
        ('Benue', 'Benue'),
        ('Borno', 'Borno'),
        ('Cross River', 'Cross River'),
        ('Delta', 'Delta'),
        ('Ebonyi', 'Ebonyi'),
        ('Enugu', 'Enugu'),
        ('Edo' , 'Edo'),
        ('Ekiti', 'Ekiti'),
        ('FCT', 'FCT'),
        ('Gombe', 'Gombe'),
        ('Imo', 'Imo'),
        ('Jigawa', 'Jigawa'),
        ('Kaduna', 'Kaduna'),
        ('Kano', 'Kano'),
        ('Kebbi', 'Kebbi'),
        ('Kogi' , 'Kogi'),
        ('Kwara', 'Kwara'),
        ('Lagos', 'Lagos'),
        ('Nasarawa', 'Nasarawa'),
        ('Niger', 'Niger'),
        ('Ogun', 'Ogun'),
        ('Ondo', 'Ondo'),
        ('Osun', 'Osun'),
        ('Oyo', 'Oyo'),
        ('Plateau', 'Plateau'),
        ('Rivers', 'Rivers'),
        ('Sokoto', 'Sokoto'),
        ('Taraba', 'Taraba'),
        ('Yobe', 'Yobe'),
        ('Zamfara', 'Zamfara'),
        )

APPLICATION_TYPE = (
        ('New Registration', 'New Registration' ),
        ('Renewal', 'Renewal'),
        )

APPLICATION_CATEGORY = (
        ('Radiography Practice Permit', 'Radiography Practice Permit'),
        ('Pri Internship Accreditation', 'Non-Teaching Hospitals Internship Accreditation'),
        ('Gov Internship Accreditation' , 'Teaching Hospitals Internship Accreditation'),
        ('Radiography Practice Permit Renewal', 'Radiography Practice Permit Renewal'),
        ('Pri Internship Accreditation Renewal', 'Non-Teaching Hospitals Internship Accreditation Renewal'),
        ('Gov Internship Accreditation Renewal', 'Teaching Hospitals Internship Accreditation Renewal'),
        )


SERVICES = (
        ('Diagnostic only', 'Diagnostic only' ),
        ('Therapeutic only', 'Therapeutic only'),
        ('Diagnostic and Therapeutic', 'Diagnostic and Therapeutic'),
        )


EQUIPMENT = (
        ('Ultrasound', 'Ultrasound' ),
        ('Conventional X-ray', 'Conventional X-ray'),
        ('Fluoroscopy', 'Fluoroscopy' ),
        ('CT Scan', 'CT Scan' ),
        ('C-Arm/O-ARM', 'C-Arm/O-ARM' ),
        ('MRI', 'MRI'),
        ('Mamography', 'Mamography' ),
        ('Angiography', 'Angiography'),
        ('Dental X-ray', 'Dental X-ray' ),
        ('Echocardiography', 'Echocardiography'),
        ('Radiotherapy', 'Radiotherapy'),
        ('Nuclear Medicine', 'Nuclear Medicine'),
        )

PAYMENT_METHOD = (
        ('Bank', 'Bank'),
        ('Card', 'Card'),        
        )


INSPECTION_ZONE = (
        ('Abuja', 'Abuja'), 
        ('Enugu', 'Enugu'), 
        ('Lagos', 'Lagos'), 
        ('Sokoto', 'Sokoto'), 
        ('Kano', 'Kano'), 
        ('Port Harcourt', 'Port Harcourt'), 
        ('Awka', 'Awka'), 
        ('Calabar', 'Calabar'), 
        ('Ilesha', 'Ilesha'), 
        ('Maiduguri', 'Maiduguri'), 
        )


VISITATION_REASON = ( 
        ('Sensitization', 'Sensitization'), 
        ('Enforcement', 'Enforcement'), 
        )

LICENSE_STATUS = (
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        )

HOSPITAL_TYPE = (
        ('Radiography Practice', 'Radiography Practice'),
        ('Internship Accreditation', 'Internship Accreditation'),
        )
