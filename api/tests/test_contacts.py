def test_list_contacts(self):
    """Agent should see only their own contacts."""

    # --- Create agent1 ---
    agent1 = User.objects.create_user(
        username="agent1@example.com",
        email="agent1@example.com",
        password="testpassword"
    )
    agent1_profile = agent1.agent_profile   # auto-created by signal

    # Login agent1
    login1 = self.client.post(reverse("login_user"), {
        "email": "agent1@example.com",
        "password": "testpassword"
    })
    token1 = login1.data["access"]
    self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")

    # Create a contact for agent1
    self.client.post(self.list_url, {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "555-1111",
        "source_id": self.source.id,
    }, format="json")

    # --- Create agent2 ---
    agent2 = User.objects.create_user(
        username="agent2@example.com",
        email="agent2@example.com",
        password="testpassword"
    )
    agent2_profile = agent2.agent_profile  # auto-created

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
        "source_id": self.source.id,
    }, format="json")
    self.assertEqual(res2.status_code, 201)

    # --- Switch back to agent1 ---
    login1b = self.client.post(reverse("login_user"), {
        "email": "agent1@example.com",
        "password": "testpassword"
    })
    token1b = login1b.data["access"]
    self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1b}")

    # Agent1 should only see their one contact
    res = self.client.get(self.list_url)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(len(res.data["results"]), 1)
