MAYBE_BOOLEAN = [
    ('NOTHING', 'unknown'),
    ('JUST_TRUE', 'yes'),
    ('JUST_FALSE', 'false'),
]


STATUS_OF_CHARGES = [
    ('UNKNOWN', 'unknown'),
    ('DETAINED_NO_PROCESSING', 'detained and released without being processed'),
    ('ARRESTED_NO_CHARGE', 'arrested but not charged'),
    ('CHARGES_PENDING', 'charges pending'),
    ('CHARGES_DROPPED', 'charges dropped'),
    ('CONVICTED', 'convicted'),
    ('ACQUITTED', 'acquitted'),
    ('PENDING_APPEAL', 'pending appeal'),
]


STATUS_OF_SEIZED_EQUIPMENT = [
    ('UNKNOWN', 'unknown'),
    ('CUSTODY', 'in custody'),
    ('RETURNED', 'returned'),
    ('RETURNED_BUT', 'returned but film or SIM cards retained'),
]


ACTORS = [
    ('LAW', 'law enforcement'),
    ('SECURITY', 'private security'),
    ('CITIZEN', 'private citizen'),
]

CITIZENSHIP_STATUS_CHOICES = [
    ('US_CITIZEN', 'U.S. citizen'),
    ('PERMANENT_RESIDENT', 'permanent resident (green card)'),
    ('IMMIGRANT_VISA', 'immigrant visa'),
    ('OTHER_VALID_VISA', 'other valid visa'),
    ('UNDOCUMENTED', 'undocumented immigrant (including visa overstays)'),
]


ASSAILANT = [
    ('LAW_ENFORCEMENT', 'law enforcement'),
    ('PRIVATE_SECURITY', 'private security'),
    ('PRIVATE_INDIVIDUAL', 'private individual'),
]


INJURY_SEVERITY = [
    ('MINOR', 'minor'),
    ('MODERATE', 'moderate'),
    ('SERIOUS', 'serious'),
    ('SEVERE', 'severe'),
    ('CRITICAL', 'critical'),
    ('FATAL', 'fatal'),
]


SUBPOENA_SUBJECT = [
    ('JOURNALIST', 'journalist'),
    ('NEWS_ORGANIZATION', 'news organization'),
    ('TECHNOLOGY', 'technology/communications company'),
    ('FINANCIAL', 'bank/financial institution'),
    ('OTHER', 'other'),
]


SUBPOENA_TYPE = [
    ('TESTIMONY_ABOUT_SOURCE', 'testimony about confidential source'),
    ('OTHER_TESTIMONY', 'other testimony'),
    ('JOURNALIST_COMMUNICATIONS', 'journalist communications or work product'),
]


SUBPOENA_STATUS = [
    ('PENDING', 'pending'),
    ('DROPPED', 'dropped'),
    ('QUASHED', 'quashed'),
    ('UPHELD', 'upheld'),
    ('CARRIED_OUT', 'carried out'),
]


CONTEMPT_STATUS = [
    ('NOT_HELD', 'not held in contempt'),
    ('THREATENED', 'threatened with contempt'),
    ('HELD_NOT_JAILED', 'held in contempt but not jailed'),
    ('HELD_AND_JAILED', 'held in contempt and jailed'),
]
