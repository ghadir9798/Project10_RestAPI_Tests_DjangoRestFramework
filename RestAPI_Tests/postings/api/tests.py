from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_jwt.settings import api_settings
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse as api_reverse

from postings.models import BlogPost

payload_handler = api_settings.JWT_PAYLOAD_HANDLER
encode_handler  = api_settings.JWT_ENCODE_HANDLER

User = get_user_model()

class BlogPostAPITestCase(APITestCase):
    def setUp(self):
        user_obj = User(username='ghadir9798', email='test@test.com')
        user_obj.set_password("somerandompassword")
        user_obj.save()
        blog_post = BlogPost.objects.create(
                user=user_obj, 
                title='New title', 
                content='some_random_content'
                )

    def test_single_user(self):
        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_single_post(self):
        post_count = BlogPost.objects.count()
        self.assertEqual(post_count, 1)

    def test_get_list(self):
        # test the get list
        data = {}
        url = api_reverse("api-postings:post-listcreate")
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.data)

    def test_post_item(self):
        # test the get list
        data = {"title": "Some random title", "content": "some more content"}
        url = api_reverse("api-postings:post-listcreate")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_get_item(self):
        # test the get list
        blog_post = BlogPost.objects.first()
        data = {}
        url = blog_post.get_api_url()
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_item(self):
        # test the get list
        blog_post = BlogPost.objects.first()
        url = blog_post.get_api_url()
        data = {"title": "Update the title", "content": "Updated Content"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_update_item_with_user(self):
        # test the get list
        blog_post = BlogPost.objects.first()
        #print(blog_post.content)
        url = blog_post.get_api_url()
        data = {"title": "Update title by Authorized User", "content": "Update Content by Authorized User"}
        user_obj = User.objects.first()
        payload  = payload_handler(user_obj)
        token_response = encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token_response)    # JWT <token>
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #print(response.data)

    def test_post_item_with_user(self):
        # test the get list
        user_obj = User.objects.first()
        payload  = payload_handler(user_obj)
        token_response = encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token_response)
        data = {"title": "Posted Title by Authorized User", "content": "Posted Content by Authorized User"}
        url = api_reverse("api-postings:post-listcreate")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_user_ownership(self):
        # test the get list
        owner = User.objects.create(username='testuser1')
        blog_post = BlogPost.objects.create(
                user=owner, 
                title='New title by owner', 
                content='some_random_content by owner'
                )
        user_obj            = User.objects.first()
        self.assertNotEqual(user_obj.username, owner.username)
        payload             = payload_handler(user_obj)
        token_response           = encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token_response)
        url = blog_post.get_api_url()
        data = {"title": "Some Title by another User", "content": "Some Content by another User"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_login_and_update(self):
        data = {
            'username': 'ghadir9798',
            'password': 'somerandompassword'
            }
        url = api_reverse("api-login")
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data.get("token")
        if token is not None:
            blog_post = BlogPost.objects.first()
            #print(blog_post.content)
            url = blog_post.get_api_url()
            data = {"title": "Some Title by logged-in User", "content": "Some Content by logged-in User"}
            self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token)     # JWT <token>
            response = self.client.put(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)  


# request.post(url, data, headers={"Authorization": "JWT " + <token> })