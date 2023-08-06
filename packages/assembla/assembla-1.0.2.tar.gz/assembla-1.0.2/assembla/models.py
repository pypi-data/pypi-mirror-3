from base_models import *
from error import AssemblaError


class API(APIObject):
    def __init__(self, auth=None, *args, **kwargs):
        """
        :auth is a required argument which should be in the format:
            `('Username', 'Password',)`
        """
        super(API, self).__init__(*args, **kwargs)
        if not auth:
            raise AssemblaError(100)
        self.auth = auth

    def check_credentials(self):
        """
        Attempt to check the authenticity of the auth credentials by retrieving
        a list of the user's spaces. Returns True on success.
        """
        if not self.spaces():
            raise AssemblaError(110)
        else:
            return True

    def spaces(self):
        """
        Return the spaces available to the user, each space is instantiated as
        a Space
        """
        raw_data = self._harvest(
            url=Space().list_url(),
            )
        return [
            Space(
                auth=self.auth,
                initialise_with=data[1]
                ) for data in raw_data
            ]


class Space(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'id'
        relative_url = 'spaces/{pk}'
        relative_list_url = 'spaces/my_spaces'

    def milestones(self):
        """
        Return the milestones in the space
        """
        url = Milestone(space=self).list_url()
        raw_data = self._harvest(url=url)
        return [
            Milestone(
                space=self,
                initialise_with=data[1]
                ) for data in raw_data
            ]

    def tickets(self):
        """
        Return the tickets in the space
        """
        url = Ticket(space=self).list_url()
        raw_data = self._harvest(url=url)
        return [
            Ticket(
                space=self,
                initialise_with=data[1]
                ) for data in raw_data
            ]

    def users(self):
        """
        Return the users in the space
        """
        url = User(space=self).list_url()
        raw_data = self._harvest(url=url)
        return [
            User(
                space=self,
                initialise_with=data[1]
                ) for data in raw_data
            ]


class Milestone(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'id'
        relative_url = 'spaces/{space}/milestones/{pk}'
        relative_list_url = 'spaces/{space}/milestones'

    def tickets(self):
        """
        Return the tickets in the milestone
        """
        return filter(
            lambda ticket: ticket.milestone_id == self.id,
            self.space.tickets(),
            )


class User(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'id'
        relative_url = 'profile/{pk}'
        relative_list_url = 'spaces/{space}/users'

    def tickets(self):
        """
        Return the tickets in the space which are assigned to the user
        """
        return filter(
            lambda ticket: ticket.assigned_to_id == self.id,
            self.space.tickets(),
            )


class Ticket(AssemblaObject):
    class Meta(APIObject.Meta):
        primary_key = 'number'
        relative_url = 'spaces/{space}/tickets/{pk}'
        relative_list_url = 'spaces/{space}/tickets'