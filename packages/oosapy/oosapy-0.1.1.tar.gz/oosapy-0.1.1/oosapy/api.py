# oosapy
# Copyright 11870.com
# See LICENSE for details.

from error import OosApyError
import models

class API:
    """Class to handle the 11870.com API
    
    auth_handler -- object that handles the authentication. It must be an
    instance of AnonymousAuthentication or OAuthAuthentication
    
    """
    
    API_HOST = 'api.11870.com'
    API_ROOT = '/api/v2'
    ROOT_URL = 'http://' + API_HOST + API_ROOT
    
    
    def __init__(self, auth_handler):
        self.auth_handler = auth_handler
        self.get_me()
    
    
    def is_authorized(self, user):
        """Check if the API is authorized to access the given user data."""
        return not self.auth_handler.is_anonymous() and\
                self.user.slug == user.slug
    
    
    def search(self, parameters):
        """Make a search over the 11870.com API. The parameters explained in
        the documentation are passed through a dictionary."""
        url = self.ROOT_URL + "/search"
        resp = self.auth_handler.get_response(url, parameters=parameters)
        return models.SearchedService.parse(self, resp[1])
    
    
    def get_me(self):
        """Return the information of the authorized user."""
        if self.auth_handler.is_anonymous():
            self.user = None
        elif self.__dict__.get("user") == None:
            url = self.ROOT_URL + "/users"
            resp = self.auth_handler.get_response(url)
            users = models.User.parse(self, resp[1])
            self.user = users[0]
        return self.user
    
    
    def get_user(self, slug):
        """Return the information of one user."""
        url = self.ROOT_URL + "/users/" + slug
        resp = self.auth_handler.get_response(url)
        return models.User.parse(self, resp[1])
    
    
    def update_user(self, user):
        """Update the user"""
        if not self.is_authorized(user):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/users/" + user.slug
        self.auth_handler.get_response(url, method="PUT", body=user.to_atom())
        return True
    
    
    def get_user_contacts(self, user):
        """Return the contacts that the user is following."""
        url = self.ROOT_URL + "/contacts/" + user.slug
        resp = self.auth_handler.get_response(url)
        return models.Contact.parse(self, resp[1])
    
    
    def get_user_activity(self, user, social=False):
        """Return the user activity. If social is set to True also the activity
        of his contacts is retrieved."""
        path = "/social-activity/" if social else "/activity/"
        url = self.ROOT_URL + path + user.slug
        resp = self.auth_handler.get_response(url)
        return models.Activity.parse(self, resp[1])
    
    
    def get_user_reviews(self, user):
        """Return the reviews of the user with its service."""
        url = self.ROOT_URL + "/sites/" + user.slug
        resp = self.auth_handler.get_response(url)
        return models.ServiceReview.parse(self, resp[1])
    
    
    def create_review(self, review):
        """Create a new review and return it."""
        if not self.is_authorized(review.user):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/sites/" + review.user.slug
        resp = self.auth_handler.get_response(url, method="POST",
                                              body=review.to_atom())
        
        return models.ServiceReview.parse(self, resp[1])
    
    
    def update_review(self, review):
        """Update a review."""
        if not self.is_authorized(review.user):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/sites/" + review.user.slug+ "/" +\
                review.service.slug
        
        self.auth_handler.get_response(url, method="PUT", body=review.to_atom())
        return True
    
    
    def delete_user_review(self, service_review):
        """Delete a review."""
        if not self.is_authorized(service_review.user):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/sites/" + service_review.user.slug + "/" +\
                service_review.service.slug
        self.auth_handler.get_response(url, method="DELETE")
        return True
    
    
    def create_contact(self, contact):
        """Create a new contact relationship and return it."""
        if not self.is_authorized(contact.fan):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/contacts/" + contact.fan.slug
        
        resp = self.auth_handler.get_response(url, method="POST",
                                              body=contact.to_atom())

        return models.Contact.parse(self, resp[1])
    
    
    def update_contact(self, contact):
        """Update the contact relationship."""
        if not self.is_authorized(contact.fan):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/contacts/" + contact.fan.slug + "/" +\
                contact.guru.slug
        
        self.auth_handler.get_response(url, method="PUT",
                                       body=contact.to_atom())
        return True
    
    
    def delete_contact(self, contact):
        """Delete a contact relationship."""
        if not self.is_authorized(contact.fan):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/contacts/" + contact.fan.slug + "/" +\
                contact.guru.slug
        self.auth_handler.get_response(url, method="DELETE")
        return True
    
    
    def get_user_avatar(self, user):
        """Return the user avatar in a file."""
        url = self.ROOT_URL + "/users/" + user.slug + "/avatar"
        resp = self.auth_handler.get_response(url)
        return resp[1]
    
    
    def update_user_avatar(self, user, avatar_file, content_type="image/jpeg"):
        """Update the user avatar with the given file."""
        if not self.is_authorized(user):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/users/" + user.slug + "/avatar"
        self.auth_handler.get_response(url, method="PUT", 
                                       body=avatar_file.read(), 
                                       headers={"Content-Type": content_type})
        return True
    
    
    def make_check_in(self, user, service, latitude, longitude):
        """Make a new check-in for the user in the given place."""
        if not self.is_authorized(user):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/checkins/user/" + user.slug
        params = "serviceSlug=%s&latitude=%f&longitude=%f" %\
                    (service.slug, latitude, longitude)
        content_type = "application/x-www-form-urlencoded"
        
        self.auth_handler.get_response(url, method="POST", body=params, 
                                       headers={"Content-Type": content_type})
        return True
    
    
    def get_user_check_ins(self, user):
        """Return the user check-ins."""
        url = self.ROOT_URL + "/checkins/user/" + user.slug
        resp = self.auth_handler.get_response(url)
        return models.CheckIn.parse(self, resp[1])
    
    
    def get_service_check_ins(self, service):
        """Return the check-ins made in a place."""
        url = self.ROOT_URL + "/checkins/site/" + service.slug
        resp = self.auth_handler.get_response(url)
        return models.CheckIn.parse(self, resp[1])
    
    
    def get_service(self, slug):
        """Return the information of a service."""
        url = self.ROOT_URL + "/site-details/" + slug
        resp = self.auth_handler.get_response(url)
        services = models.Service.parse(self, resp[1])
        return services[0]
    
    
    def get_service_reviews(self, service):
        """Return the reviews of a service."""
        url = self.ROOT_URL + "/site-reviews/" + service.slug
        resp = self.auth_handler.get_response(url)
        return models.ServiceReview.parse(self, resp[1])
    
    
    def get_review_media(self, service_review):
        """Return the media entries of a review."""
        url = self.ROOT_URL + "/sites/" + service_review.user.slug + "/" +\
                service_review.service.slug + "/media"
        resp = self.auth_handler.get_response(url)
        
        medias = models.Media.parse(self, resp[1])
        for media in medias:
            media.set_service(service_review.service)
        return medias
    
    
    def get_media_file(self, media):
        """Return the media in a file."""
        url = self.ROOT_URL + "/sites/" + media.user.slug + "/" +\
                media.service.slug + "/media/" + media.fnv
        resp = self.auth_handler.get_response(url)
        return resp[1]
    
    
    def create_media(self, media, file, content_type="image/jpeg"):
        """Create a new media and return its entry."""
        if not self.is_authorized(media.user):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/sites/" + media.user.slug + "/" +\
                media.service.slug + "/media"
        resp = self.auth_handler.get_response(
                                url, method="POST",
                                body=file.read(),
                                headers={"Content-Type": content_type})
        
        media_returned = models.Media.parse(self, resp[1])
        media_returned.set_service(media.service)
        return media_returned
    
    
    def update_media(self, media):
        """Update the media metadata."""
        if not self.is_authorized(media.user):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/sites/" + media.user.slug + "/" +\
                media.service.slug + "/media/" + media.fnv + ".atom"
        self.auth_handler.get_response(url, method="PUT", body=media.to_atom())
        return True
    
    
    def delete_media(self, media):
        """Delete the media."""
        if not self.is_authorized(media.user):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/sites/" + media.user.slug + "/" +\
                media.service.slug + "/media/" + media.fnv
        self.auth_handler.get_response(url, method="DELETE")
        return True
    
    
    def get_tags(self, user):
        """Return the tags of a user."""
        if not self.is_authorized(user):
            raise OosApyError("Authentication error")
        
        url = self.ROOT_URL + "/tags/" + user.slug
        resp = self.auth_handler.get_response(url)
        return models.Tag.parse(self, resp[1])
    
    
    def get_lists(self, user):
        """Return the lists of a user."""
        if not self.is_authorized(user):
            return False
        
        url = self.ROOT_URL + "/lists/" + user.slug
        resp = self.auth_handler.get_response(url)
        return models.List.parse(self, resp[1])
    
    
    def get_categories(self):
        """Return the 11870.com categories."""
        url = self.ROOT_URL + "/categories"
        resp = self.auth_handler.get_response(url)
        return models.Category.parse(self, resp[1])
    
    
    def get_attributes(self):
        """Return the 11870.com attributes."""
        url = self.ROOT_URL + "/attributes"
        resp = self.auth_handler.get_response(url)
        return models.Attribute.parse(self, resp[1])
    
    
    def get_privacy(self):
        """Return the allowed values for privacy."""
        url = self.ROOT_URL + "/privacy"
        resp = self.auth_handler.get_response(url)
        return models.Privacy.parse(self, resp[1])
    
    
    def get_trusted(self):
        """Return the allowed values for trusted."""
        url = self.ROOT_URL + "/trusted"
        resp = self.auth_handler.get_response(url)
        return models.Trusted.parse(self, resp[1])
    
    