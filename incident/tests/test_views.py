import csv
import io
from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from incident.models import choices
from incident.tests.factories import (
    IncidentPageFactory,
)


User = get_user_model()


class LegalOrderImportTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(
            username="test",
            password="test",
            email="test@example.com",
        )
        cls.inc1 = IncidentPageFactory()
        cls.inc2 = IncidentPageFactory()
        cls.inc3 = IncidentPageFactory()

    def setUp(self):
        self.client.force_login(self.user)
        self.import_url = reverse("import_legal_orders:show_form")
        self.confirm_url = reverse("import_legal_orders:confirm")

    def post_csv(self, row_data, *args, **kwargs):
        csv_content = io.StringIO()
        fieldnames = [
            "slug",
            "venue",
            "target",
        ]
        for order_number in range(1, 5):
            fieldnames.extend(
                [
                    f"legal_order{order_number}_type",
                    f"legal_order{order_number}_information_requested",
                ]
            )
            for status_number in range(1, 5):
                fieldnames.extend(
                    [
                        f"legal_order{order_number}_status{status_number}",
                        f"legal_order{order_number}_date{status_number}",
                    ]
                )

        writer = csv.DictWriter(csv_content, fieldnames=fieldnames)
        writer.writeheader()
        for row in row_data:
            writer.writerow(row)

        # Reset file pointer for posting
        csv_content.seek(0)
        response = self.client.post(
            path=self.import_url,
            data={"name": "filename.csv", "csv_file": csv_content},
            **kwargs,
        )
        return response

    def test_getting_the_form_is_successful(self):
        response = self.client.get(self.import_url)
        self.assertEqual(response.status_code, 200)

    def test_csvs_submitted_with_nonexistent_slugs_are_invalid(self):
        invalid = "http://localhost:8000/nonexistent-slug"
        response = self.post_csv(
            [
                {
                    "slug": invalid,
                }
            ]
        )
        self.assertContains(
            response, f"Row 2, column slug: Could not locate incident at {invalid}"
        )

    def test_csvs_submitted_with_nonexistent_types_are_invalid(self):
        invalid = "invalid"
        response = self.post_csv(
            [
                {
                    "slug": self.inc1.slug,
                    "legal_order1_type": invalid,
                }
            ]
        )
        self.assertContains(
            response, f"Row 2, column legal_order1_type: {invalid} is invalid input"
        )

    def test_csvs_submitted_with_nonexistent_information_requested_are_invalid(self):
        invalid = "invalid"
        response = self.post_csv(
            [
                {
                    "slug": self.inc1.slug,
                    "legal_order1_information_requested": invalid,
                }
            ]
        )
        self.assertContains(
            response,
            f"Row 2, column legal_order1_information_requested: {invalid} is invalid input",
        )

    def test_csvs_submitted_with_nonexistent_statuses_are_invalid(self):
        invalid = "invalid"
        response = self.post_csv(
            [
                {
                    "slug": self.inc1.slug,
                    "venue": choices.LegalOrderVenue.STATE.label,
                    "target": choices.LegalOrderTarget.JOURNALIST.label,
                    "legal_order1_type": choices.LegalOrderType.SUBPOENA.label,
                    "legal_order1_information_requested": choices.InformationRequested.OTHER_TESTIMONY.label,
                    "legal_order1_status1": invalid,
                }
            ]
        )
        self.assertContains(
            response, f"Row 2, column legal_order1_status1: {invalid} is invalid input"
        )

    def test_csvs_submitted_with_invalid_dates_are_invalid(self):
        invalid = "2018-1128"
        response = self.post_csv(
            [
                {
                    "slug": self.inc1.slug,
                    "venue": choices.LegalOrderVenue.STATE.label,
                    "target": choices.LegalOrderTarget.JOURNALIST.label,
                    "legal_order1_type": choices.LegalOrderType.SUBPOENA.label,
                    "legal_order1_information_requested": choices.InformationRequested.OTHER_TESTIMONY.label,
                    "legal_order1_status1": choices.LegalOrderStatus.PENDING,
                    "legal_order1_date1": invalid,
                }
            ]
        )
        self.assertContains(
            response,
            f"Row 2, column legal_order1_date1: Invalid isoformat string: &#x27;{invalid}&#x27;",
        )

    def test_csvs_submitted_with_nonexistent_venues_are_invalid(self):
        invalid = "invalid"
        response = self.post_csv(
            [
                {
                    "slug": self.inc1.slug,
                    "legal_order1_type": choices.LegalOrderType.SUBPOENA.label,
                    "venue": invalid,
                }
            ]
        )
        self.assertContains(
            response, f"Row 2, column venue: {invalid} is invalid input"
        )

    def test_csvs_submitted_with_nonexistent_targets_are_invalid(self):
        invalid = "invalid"
        response = self.post_csv(
            [
                {
                    "slug": self.inc1.slug,
                    "legal_order1_type": choices.LegalOrderType.SUBPOENA.label,
                    "venue": choices.LegalOrderVenue.FEDERAL,
                    "target": invalid,
                }
            ]
        )
        self.assertContains(
            response, f"Row 2, column target: {invalid} is invalid input"
        )

    def test_posting_a_file_updates_the_session(self):
        venue = choices.LegalOrderVenue.STATE
        target = choices.LegalOrderTarget.JOURNALIST
        order_type = choices.LegalOrderType.SUBPOENA
        info_requested = choices.InformationRequested.OTHER_TESTIMONY
        status1 = choices.LegalOrderStatus.PENDING
        date1 = "2023-01-05"
        status2 = choices.LegalOrderStatus.QUASHED
        date2 = "2023-01-15"
        self.post_csv(
            [
                {
                    "slug": self.inc1.slug,
                    "venue": venue.label,
                    "target": target.label,
                    "legal_order1_type": order_type.label,
                    "legal_order1_information_requested": info_requested.label,
                    "legal_order1_status1": status1.label,
                    "legal_order1_date1": date1,
                    "legal_order1_status2": status2.label,
                    "legal_order1_date2": date2,
                }
            ],
            follow=True,
        )

        self.assertEqual(
            self.client.session["legal_order_import"],
            {
                str(self.inc1.pk): {
                    "venue": venue.value,
                    "target": target.value,
                    "legal_orders": [
                        {
                            "information_requested": info_requested.value,
                            "type": order_type.value,
                            "statuses": [
                                {
                                    "date": date1,
                                    "status": status1.value,
                                },
                                {
                                    "date": date2,
                                    "status": status2.value,
                                },
                            ],
                        }
                    ],
                }
            },
        )

    def test_posting_a_file_with_missing_update_dates_updates_the_session(self):
        venue = choices.LegalOrderVenue.STATE
        target = choices.LegalOrderTarget.JOURNALIST
        order_type = choices.LegalOrderType.SUBPOENA
        info_requested = choices.InformationRequested.OTHER_TESTIMONY
        status1 = choices.LegalOrderStatus.PENDING
        date1 = "2023-01-05"
        status2 = choices.LegalOrderStatus.QUASHED
        date2 = ""
        self.post_csv(
            [
                {
                    "slug": self.inc1.slug,
                    "venue": venue.label,
                    "target": target.label,
                    "legal_order1_type": order_type.label,
                    "legal_order1_information_requested": info_requested.label,
                    "legal_order1_status1": status1.label,
                    "legal_order1_date1": date1,
                    "legal_order1_status2": status2.label,
                    "legal_order1_date2": date2,
                }
            ],
            follow=True,
        )

        self.assertEqual(
            self.client.session["legal_order_import"],
            {
                str(self.inc1.pk): {
                    "venue": venue.value,
                    "target": target.value,
                    "legal_orders": [
                        {
                            "information_requested": info_requested.value,
                            "type": order_type.value,
                            "statuses": [
                                {
                                    "date": date1,
                                    "status": status1.value,
                                },
                                {
                                    "date": None,
                                    "status": status2.value,
                                },
                            ],
                        }
                    ],
                }
            },
        )

    def test_confirming_a_file_a_file_updates_the_incident(self):
        venue = choices.LegalOrderVenue.STATE
        target = choices.LegalOrderTarget.JOURNALIST
        order_type = choices.LegalOrderType.SUBPOENA
        info_requested = choices.InformationRequested.OTHER_TESTIMONY
        status1 = choices.LegalOrderStatus.PENDING
        date1 = date(2023, 1, 5)
        status2 = choices.LegalOrderStatus.QUASHED
        date2 = date(2023, 1, 15)

        session = self.client.session

        session["legal_order_import"] = {
            str(self.inc1.pk): {
                "venue": venue.value,
                "target": target.value,
                "legal_orders": [
                    {
                        "information_requested": info_requested.value,
                        "type": order_type.value,
                        "statuses": [
                            {
                                "date": str(date1),
                                "status": status1.value,
                            },
                            {
                                "date": str(date2),
                                "status": status2.value,
                            },
                        ],
                    }
                ],
            }
        }
        session.save()
        response = self.client.post(self.confirm_url)
        self.assertRedirects(
            response,
            reverse("import_legal_orders:show_form"),
        )

        # Successful import removes the corresponding session data
        self.assertNotIn("legal_order_import", self.client.session)

        self.inc1.refresh_from_db()
        self.assertEqual(self.inc1.legal_order_venue, venue)
        self.assertEqual(self.inc1.legal_order_target, target)
        legal_order = self.inc1.legal_orders.all()[0]
        self.assertEqual(legal_order.information_requested, info_requested)
        self.assertEqual(legal_order.order_type, order_type)
        self.assertEqual(legal_order.status, status1)
        self.assertEqual(legal_order.date, date1)
        update = legal_order.updates.all()[0]
        self.assertEqual(update.status, status2)
        self.assertEqual(update.date, date2)

    def test_confirming_a_file_with_missing_update_date_updates_the_incident(self):
        venue = choices.LegalOrderVenue.STATE
        target = choices.LegalOrderTarget.JOURNALIST
        order_type = choices.LegalOrderType.SUBPOENA
        info_requested = choices.InformationRequested.OTHER_TESTIMONY
        status1 = choices.LegalOrderStatus.PENDING
        date1 = date(2023, 1, 5)
        status2 = choices.LegalOrderStatus.QUASHED
        date2 = None

        session = self.client.session

        session["legal_order_import"] = {
            str(self.inc1.pk): {
                "venue": venue.value,
                "target": target.value,
                "legal_orders": [
                    {
                        "information_requested": info_requested.value,
                        "type": order_type.value,
                        "statuses": [
                            {
                                "date": str(date1),
                                "status": status1.value,
                            },
                            {
                                "date": date2,
                                "status": status2.value,
                            },
                        ],
                    }
                ],
            }
        }
        session.save()
        response = self.client.post(self.confirm_url)
        self.assertRedirects(
            response,
            reverse("import_legal_orders:show_form"),
        )
        # self.assertEqual(response.status_code, )

        # Successful import removes the corresponding session data
        self.assertNotIn("legal_order_import", self.client.session)

        self.inc1.refresh_from_db()
        self.assertEqual(self.inc1.legal_order_venue, venue)
        self.assertEqual(self.inc1.legal_order_target, target)
        legal_order = self.inc1.legal_orders.all()[0]
        self.assertEqual(legal_order.information_requested, info_requested)
        self.assertEqual(legal_order.order_type, order_type)
        self.assertEqual(legal_order.status, status1)
        self.assertEqual(legal_order.date, date1)
        update = legal_order.updates.all()[0]
        self.assertEqual(update.status, status2)
        self.assertEqual(update.date, date2)
