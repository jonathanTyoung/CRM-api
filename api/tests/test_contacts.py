def test_list_contacts(self):
    """Agent should see only their own contacts"""

    # Create a contact for agent1
    self.client.post(self.list_url, self.payload, format="json")

    # Create agent2 + contact owned by agent2
    agent2 = User.objects.create_user(
        username="agent2@example.com",
        email="agent2@example.com",
        password="testpassword"
    )

    # Login agent2
    login2 = self.client.post(reverse("login_user"), {
        "email": "agent2@example.com",
        "password": "testpassword"
    })
    token2 = login2.data["access"]
    self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")

    # Create a contact for agent2
    res2 = self.client.post(self.list_url, {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "phone": "555-2222",
        "source_id": self.source.id,   # 🔥 FIXED
    }, format="json")
    self.assertEqual(res2.status_code, 201)  # 🔥 ensure the contact was created

    # Login back as agent1
    login1 = self.client.post(reverse("login_user"), {
        "email": "agent1@example.com",
        "password": "testpassword"
    })
    token1 = login1.data["access"]
    self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")

    res = self.client.get(self.list_url)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(len(res.data["results"]), 1)
