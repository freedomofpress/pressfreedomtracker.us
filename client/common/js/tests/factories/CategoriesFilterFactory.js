export const CATEGORIES_FILTER = [
  {
    'filters': [
      {'name': 'search', 'title': 'Search terms', 'type': 'text'},
      {'name': 'date', 'title': 'Took place between', 'type': 'date'}
    ],
    'id': -1,
    'title': 'General'
  },
  {
    'filters': [
      {
        'name': 'charged_under_espionage_act',
        'title': 'Charged under espionage act?',
        'type': 'bool'
      }
    ],
    'id': 5,
    'title': 'Leak Case',
    'url': '/leak_case/'
  },
  {
    'filters': [
      {
        'choices': [
          ('PENDING', 'pending'),
          ('DROPPED', 'dropped'),
          ('STRUCK_DOWN', 'struck down'),
          ('UPHELD', 'upheld'),
          ('IGNORED', 'ignored')
        ],
        'name': 'status_of_prior_restraint',
        'title': 'Status of prior restraint',
        'type': 'choice'
      }
    ],
    'id': 6,
    'title': 'Prior Restraint',
    'url': '/prior_restraint/'
  },
  {
    'filters': [],
    'id': 7,
    'title': 'Other Incident',
    'url': '/other_incident/'
  },
  {
    'filters': [
      {
        'choices': [
          ('UNKNOWN', 'unknown'),
          ('DETAINED_NO_PROCESSING',
            'detained and released without being processed'),
          ('DETAINED_CUSTODY',
            'detained and still in custody'),
          ('ARRESTED_CUSTODY',
            'arrested and still in custody'),
          ('ARRESTED_RELEASED', 'arrested and released')
        ],
        'name': 'arrest_status',
        'title': 'Arrest status',
        'type': 'choice'
      },
      {
        'choices': [
          ('UNKNOWN', 'unknown'),
          ('NOT_CHARGED', 'not charged'),
          ('CHARGES_PENDING', 'charges pending'),
          ('CHARGES_DROPPED', 'charges dropped'),
          ('CONVICTED', 'convicted'),
          ('ACQUITTED', 'acquitted'),
          ('PENDING_APPEAL', 'pending appeal')
        ],
        'name': 'status_of_charges',
        'title': 'Status of charges',
        'type': 'choice'
      },
      {
        'name': 'detention_date',
        'title': 'Detention date between',
        'type': 'date'
      },
      {
        'name': 'release_date',
        'title': 'Release date between',
        'type': 'date'
      },
      {
        'name': 'unnecessary_use_of_force',
        'title': 'Unnecessary use of force?',
        'type': 'bool'
      }
    ],
   'id': 8,
   'title': 'Arrest / Criminal Charge',
   'url': '/arrest/'},
  {
    'filters': [
      {
        'choices': [
          ('UNKNOWN', 'unknown'),
          ('LAW_ENFORCEMENT', 'law enforcement'),
          ('PRIVATE_SECURITY', 'private security'),
          ('POLITICIAN', 'politician'),
          ('PUBLIC_FIGURE', 'public figure'),
          ('PRIVATE_INDIVIDUAL', 'private individual')
        ],
        'name': 'assailant',
        'title': 'Assailant',
        'type': 'choice'
      },
      {
        'name': 'was_journalist_targeted',
        'title': 'Was journalist targeted?',
        'type': 'radio'
      }
    ],
    'id': 14,
    'title': 'Physical Attack',
    'url': '/physical_attack/'
  }
]
