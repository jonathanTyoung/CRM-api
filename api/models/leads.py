from django.db import models
from django.contrib.auth.models import User
from .contacts import Contact
from .sources import Source
from .lead_groups import LeadGroup

class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('nurturing', 'Nurturing'),
        ('appointment_set', 'Appointment Set'),
        ('appointment_held', 'Appointment Held'),
        ('agreement_signed', 'Agreement Signed'),
        ('listed_or_showing', 'Listed/Showing'),
        ('contract_accepted', 'Contract Accepted'),
        ('closed', 'Listed/Closed'),
    ]

    TYPE_CHOICES = [
        ('buying', 'Buying'),
        ('selling', 'Selling'),
        ('buying_and_selling', 'Buying & Selling'),
    ]

    # 🔥 Lead can stand alone without Contact (correct!)
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )

    # Basic lead info (SHOULD NOT depend on Contact)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    assigned_agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_leads'
    )

    group = models.ForeignKey(
        LeadGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )

    type = models.CharField(max_length=30, choices=TYPE_CHOICES, db_index=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        db_index=True
    )

    notes = models.TextField(blank=True)

    source = models.ForeignKey(
        Source,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Lead: {self.first_name} {self.last_name}"

    # 🔥 Conversion Logic (Lead ➜ Contact)
    def convert_to_contact(self):
        """
        Converts this Lead into a Contact and associates them.
        """
        if self.contact:
            # Lead is already converted
            return self.contact

        # Create new Contact
        new_contact = Contact.objects.create(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            phone=self.phone,
            owner=self.assigned_agent.agentprofile,  # agentprofile required
            source=self.source,
            relationship_type='prospect',
        )

        self.contact = new_contact
        self.status = 'converted'
        self.save()

        return new_contact
