from urllib import quote_plus
from django.contrib.localflavor.us.us_states import US_STATES, US_TERRITORIES
from django.contrib.localflavor.us.models import PhoneNumberField
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from sunlightcongress import choices
from sunlightcongress.managers import CommitteeManager, LegislatorManager


class Legislator(models.Model):
    """
    Legislator model
    """
    title = models.CharField(_('Title'),
        blank=True,
        null=True,
        choices=choices.TITLE_CHOICES,
        max_length=3,
    )
    firstname = models.CharField(_('First Name'),
        blank=True,
        null=True,
        max_length=64,
    )
    middlename = models.CharField(_('Middle Name'),
        blank=True,
        null=True,
        max_length=64,
    )
    lastname = models.CharField(_('Last Name'),
        blank=True,
        null=True,
        max_length=64,
    )
    name_suffix = models.CharField(_('Suffix'),
        blank=True,
        null=True,
        max_length=16,
    )
    nickname = models.CharField(_('Nickname'),
        blank=True,
        null=True,
        max_length=64,
    )
    party = models.CharField(_('Political Party'),
        blank=True,
        null=True,
        choices=choices.PARTY_CHOICES,
        max_length=1,
    )
    state = models.CharField(_('State'),
        blank=True,
        null=True,
        choices=US_STATES + US_TERRITORIES,
        max_length=2,
    )
    district = models.CharField(_('District'),
        blank=True,
        null=True,
        max_length=16,
    )
    in_office = models.BooleanField(_('Is in office?'))
    gender = models.CharField(_('Gender'),
        blank=True,
        null=True,
        choices=choices.GENDER_CHOICES,
        max_length=1,
    )
    phone = PhoneNumberField(_('Phone Number'),
        blank=True,
        null=True,
    )
    fax = PhoneNumberField(_('Fax Number'),
        blank=True,
        null=True,
    )
    website = models.URLField(_('Website'),
        blank=True,
        null=True,
        max_length=1024,
    )
    webform = models.URLField(_('Website Contact Form'),
        blank=True,
        null=True,
        max_length=1024,
    )
    email = models.EmailField(_('Email Address'),
        blank=True,
        null=True,
        max_length=254,
    )
    congress_office = models.CharField(_('Office Address'),
        blank=True,
        null=True,
        max_length=512,
    )
    bioguide_id = models.CharField(_('Congress Biographical Directory ID'),
        primary_key=True,
        max_length=32
    )
    votesmart_id = models.IntegerField(_('Votesmart ID'),
        blank=True,
        null=True,
        unique=True,
    )
    fec_id = models.CharField(_('Federal Election Commission ID'),
        blank=True,
        null=True,
        max_length=16,
        unique=True,
    )
    govtrack_id = models.IntegerField(_('GovTrack.us ID'),
        blank=True,
        null=True,
        unique=True,
    )
    crp_id = models.CharField(_('Center for Responsive Politics ID'),
        blank=True,
        null=True,
        max_length=16,
        unique=True,
    )
    congresspedia_url = models.URLField(_('Congresspedia URL'),
        blank=True,
        null=True,
        max_length=1024,
    )
    twitter_id = models.CharField(_('Twitter ID'),
        blank=True,
        null=True,
        max_length=15,
    )
    youtube_url = models.URLField(_('YouTube URL'),
        blank=True,
        null=True,
        max_length=1024,
    )
    facebook_id = models.CharField(_('Facebook ID'),
        blank=True,
        null=True,
        max_length=64,
    )
    senate_class = models.CharField(_('Senate Class'),
        blank=True,
        null=True,
        choices=choices.SENATE_CLASS_CHOICES,
        max_length=3,
    )
    official_rss = models.URLField(_('Official RSS Feed'),
        blank=True,
        null=True,
        max_length=1024,
    )
    birthdate = models.DateField(_('Birthdate'),
        blank=True,
        null=True,
    )

    def __unicode__(self):
        return u'%s (%s-%s)' % (
            self.fullname,
            self.party,
            self.state,
        )

    class Meta:
        ordering = ['lastname', 'firstname']
        verbose_name = 'Legislator'
        verbose_name_plural = 'Legislatorsf'

    objects = LegislatorManager()

    @property
    def fullname(self):
        """
        Returns the legislator's full name
        """
        return '%s. %s %s%s%s' % (
            self.title,
            self.firstname,
            '%s ' % self.middlename if self.middlename else '',
            self.lastname,
            ' %s' % self.name_suffix if self.name_suffix else '',
        )

    @property
    def house(self):
        """
        Returns the house in which the legislator serves. Delegates and
        Resident Commissioners serve in the House.
        """
        if self.title == 'Sen':
            return _('Senate')
        elif self.title == 'Rep' or self.title == 'Del' or self.title == 'Com':
            return _('House of Representatives')
        else:
            return None

    @property
    def urls(self):
        """
        Returns a dict of URLs associated with the legislator:
        - Their website
        - The contact form on their website
        - Their official RSS feed
        - Their Congressional Bioguide page
        - Their VoteSmart page
        - Their FEC report
        - Their GovTrack page
        - Their OpenSecrets page
        - Their Congresspedia page
        - Their Twitter stream
        - Their YouTube channel
        - Their Facebook page
        """
        urls = {}

        if self.website:
            urls['website'] = self.website

        if self.webform:
            urls['webform'] = self.webform

        if self.official_rss:
            urls['rss'] = self.official_rss

        if self.bioguide_id:
            urls['bioguide'] = (
                'http://bioguide.congress.gov/scripts/biodisplay.pl?'
                'index=%s' % quote_plus(self.bioguide_id)
            )

        if self.votesmart_id:
            urls['votesmart'] = 'http://votesmart.org/candidate/%s/' % \
                quote_plus(str(self.votesmart_id))

        if self.fec_id:
            urls['fec'] = 'http://query.nictusa.com/cgi-bin/can_detail/%s/' % \
                quote_plus(self.fec_id)

        if self.govtrack_id:
            name = slugify('%s %s' % (self.firstname, self.lastname,))
            urls['govtrack'] = (
                'http://www.govtrack.us/congress/members/%s/%s' % (
                    quote_plus(name.replace('-', '_')),
                    quote_plus(str(self.govtrack_id)),
                )
            )

        if self.crp_id:
            urls['opensecrets'] = (
                'http://www.opensecrets.org/politicians/summary.php?cid=%s' %
                quote_plus(self.crp_id)
            )

        if self.congresspedia_url:
            urls['congresspedia'] = self.congresspedia_url

        if self.twitter_id:
            urls['twitter'] = 'https://twitter.com/%s' % \
                quote_plus(self.twitter_id)

        if self.youtube_url:
            urls['youtube'] = self.youtube_url

        if self.facebook_id:
            urls['facebook'] = 'https://www.facebook.com/%s' % \
                quote_plus(self.facebook_id)

        return urls


class Committee(models.Model):
    """
    Committee model
    """
    id = models.CharField(_('Committee ID'),
        primary_key=True,
        max_length=6,
    )
    chamber = models.CharField(_('Chamber'),
        blank=True,
        null=True,
        choices=choices.CHAMBER_CHOICES,
        max_length=6,
    )
    name = models.CharField(_('Name'),
        blank=True,
        null=True,
        max_length=128,
    )
    parent = models.ForeignKey('self', null=True)
    members = models.ManyToManyField(Legislator)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Committee'
        verbose_name_plural = 'Committees'

    objects = CommitteeManager()
