"Campfire client"
from pinder.connector import HTTPConnector
from pinder.exc import RoomNotFoundException
from pinder.room import Room

VERSION = "1.0b"
USER_AGENT = "Pinder/%s" % VERSION

class Campfire(object):
    """Initialize a Campfire client with the given subdomain and token.
     Accepts a third boolean parameter to enable SSL (defaults to false)."""
    def __init__(self, subdomain, token, ssl=False, connector=HTTPConnector):
        # The Campfire's subdomain.
        self.subdomain = subdomain
        self._token = token
        connector = connector or HTTPConnector
        self._connector = connector(
            subdomain, token, ssl, ua=USER_AGENT)
        # The URI object of the Campfire account.
        self.uri = self._connector.uri

    def rooms(self):
        "Returns the rooms available in the Campfire account"
        return self._connector.get('rooms')['rooms']

    def joined_rooms(self):
        "Returns the rooms you've joined"
        return self._connector.get('presence')['rooms']
    rooms_joined = joined_rooms

    def rooms_names(self):
        "Returns the rooms names available in the Campfire account"
        rooms = self._connector.get('rooms')['rooms']
        return sorted([room['name'] for room in rooms])
        
    def room(self, room_id):
        "Returns the room info for the room with the given id."
        data = self._connector.get("room/%s" % room_id)
        if not data:
            raise RoomNotFoundException("The room %s does not exist." % room_id)
        return Room(self, room_id, data['room'], connector=self._connector)

    def find_room_by_name(self, name):
        """Finds a Campfire room with the given name.
        
        Returns a Room instance if found, None otherwise."""
        rooms = self.rooms()
        for room in rooms:
            if room['name'] == name:
                return Room(self, room['id'],
                    data=room, connector=self._connector)

    def users(self, *rooms_ids):
        "Returns info about users in any room or in the given room(s)."
        rooms = self.rooms()
        users = []
        for room in rooms:
            if not rooms_ids or room['id'] in rooms_ids:
                if room.get('users'):
                    users.append(room.get('users'))
        return users
        
    def user(self, user_id):
        "Returns info about the user with the given user_id."
        return self._connector.get("users/%s" % user_id)
        
    def me(self):
        "Returns info about the authenticated user."
        return self._connector.get("users/me")['user']
        
    def search(self, term):
        "Returns all the messages containing the given term."
        return self._connector.get("search/%s" % term)['messages']
