from django.db import models, transaction

from sunlight import congress

from sunlightcongress.choices import CHAMBER_CHOICES


class LegislatorManager(models.Manager):
    """
    Custom manager for the Legislator model which adds the following methods:

    fetch() - compares and updates all Legislator objects against the data
        contained within the Sunlight Foundation's Congress API.
    for_zip(zip_code) - returns a QuerySet of all legislators serving the
        passed zip code
    for_lat_lng(latitude, longitude) - returns a QuerySet of all legislators
        serving the passed coordinates
    """

    def fetch(self):
        """
        Compares and updates all Legislator objects against the data contained
        within the Sunlight Foundation's Congress API.

        The entire operation is enclosed in a transaction that is only
        committed if no exceptions are raised.
        """
        with transaction.commit_manually():
            try:
                for legislator in congress.legislators():
                    legislator_obj = self.get_or_create(
                        bioguide_id=legislator['bioguide_id']
                    )[0]
                    for name, value in legislator.iteritems():
                        setattr(legislator_obj, name, value)
                    legislator_obj.save()
            except Exception as e:
                transaction.rollback()
                raise e
            else:
                transaction.commit()

    def for_zip(self, zip_code):
        """
        Returns a QuerySet of all legislators serving the passed zip code.

        Example:
        >>> Legislator.objects.for_zip(54751)
        [<Legislator: Sen. Ron Johnson (R-WI)>,
        <Legislator: Rep. Ronald Kind (D-WI)>,
        <Legislator: Sen. Herbert Kohl (D-WI)>]
        """
        legislators = congress.legislators_for_zip(zip_code)
        legislator_ids = [l['bioguide_id'] for l in legislators]
        return self.get_query_set().filter(pk__in=legislator_ids)

    def for_lat_lng(self, latitude, longitude):
        """
        Returns a QuerySet of all legislators serving the passed coordinates.

        Example:
        >>> Legislator.objects.for_lat_lng(35.778788, -78.787805)
        [<Legislator: Sen. Richard Burr (R-NC)>,
        <Legislator: Sen. Kay Hagan (D-NC)>,
        <Legislator: Rep. David Price (D-NC)>]
        """
        legislators = congress.legislators_for_lat_lon(latitude, longitude)
        legislator_ids = [l['bioguide_id'] for l in legislators]
        return self.get_query_set().filter(pk__in=legislator_ids)


class CommitteeManager(models.Manager):
    """
    Custom manager for the Committee model which adds the following methods:

    fetch() - compares and updates all Committee objects against the data
        contained within the Sunlight Foundation's Congress API, including
        subcommittees and memberships to committees.
    """

    def fetch(self):
        """
        Compares and updates all Committee objects against the data contained
        within the Sunlight Foundation's Congress API, including subcommittees
        and memberships to committees.

        There are three steps to this method:

        1) Get or create a Committee object for each congressional committee
        2) Clear all existing Committee memberships
        3) Iterate over each legislator, fetching and creating all memberships.

        Each operation is enclosed in a transaction that is only committed if
        no exceptions are raised.
        """
        for chamber in CHAMBER_CHOICES:

            # Get or create a Committee object for each congressional committee
            for committee in congress.committees(chamber[0]):

                with transaction.commit_on_success():
                    committee_obj = self.get_or_create(
                        id=committee['id']
                    )[0]
                    for name, value in committee.iteritems():
                        setattr(committee_obj, name, value)
                    committee_obj.save()

                    # Create object for each subcommittee of the committee
                    if 'subcommittees' in committee:
                        for subcommittee in committee['subcommittees']:
                            subcommittee = subcommittee['committee']
                            subcommittee_obj = self.get_or_create(
                                id=subcommittee['id']
                            )[0]
                            for name, value in subcommittee.iteritems():
                                setattr(subcommittee_obj, name, value)
                            subcommittee_obj.parent = committee_obj
                            subcommittee_obj.save()

        # Clear all committee memberships
        with transaction.commit_on_success():
            for committee in self.all():
                committee.members.clear()
                committee.save()

        # Iterate over each legislator, fetching and creating all memberships
        Legislator = self.model._meta.get_field_by_name('members')[0].rel.to
        for legislator in Legislator.objects.all():
            leg_id = legislator.bioguide_id
            with transaction.commit_on_success():
                for committee in congress.committees_for_legislator(leg_id):
                    committee_obj = self.get(id=committee['id'])
                    committee_obj.members.add(legislator)
                    committee_obj.save()
