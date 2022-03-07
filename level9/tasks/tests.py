from django.test import TestCase, Client, RequestFactory, TestCase
from django.contrib.auth.models import User
from tasks.models import Task

class ViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.users = [
            User.objects.create_user(username="user1", email="user1@user.com", password="pass1"),
            User.objects.create_user(username="user2", email="user2@user.com", password="pass2")
        ]
    def test_views(self):
        task1 = Task.objects.create(title="This is the first task", description="hope this works", user=self.users[0])
        task2 = Task.objects.create(title="This is the second task", description="fingers crossed", user=self.users[1])
        self.client.login(username='user1', password='pass1')

        response = self.client.get(f"/update-task/{task1.pk}")
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f'/all_tasks/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/completed_tasks/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f"/delete-task/{task1.pk}")
        self.assertEqual(response.status_code, 200)

        self.client.login(username='user2', password='pass2')

        response = self.client.get(f"/update-task/{task2.pk}")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/create-task', 
            {
                'title' : 'We testing',
                'description' : 'I really hope this works',
                'priority' : 0,
                'completed' : False,
                'status' : 'PENDING'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/tasks")

        #basically checks if the task added above moves the older task's priority up by 1
        user2_task = Task.objects.get(title="Normal Task 2", user=self.users[1])
        self.assertEqual(user2_task.priority, 1)

        

