#!/usr/bin/env python3
"""Unit and integration tests for client.GithubOrgClient."""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test org returns correct payload and get_json called once."""
        expected_url = GithubOrgClient.ORG_URL.format(org=org_name)
        expected_payload = {"name": org_name, "repos_url": f"https://api.github.com/orgs/{org_name}/repos"}

        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected_payload)
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self):
        """Test _public_repos_url returns correct URL from org payload."""
        known_payload = {"repos_url": "https://api.github.com/orgs/test-org/repos"}

        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=PropertyMock,
            return_value=known_payload
        ) as mock_org:
            client = GithubOrgClient("test-org")
            self.assertEqual(client._public_repos_url, known_payload["repos_url"])
            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns correct repo names."""
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = repos_payload
        expected_repos = ["repo1", "repo2", "repo3"]
        test_url = "https://api.github.com/orgs/test/repos"

        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value=test_url
        ) as mock_public_repos_url:
            client = GithubOrgClient("test")
            result = client.public_repos()

            self.assertEqual(result, expected_repos)
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license returns correct boolean."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos using fixtures."""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get to return fixture payloads based on URL."""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            """Return org_payload for org URL, repos_payload for repos URL."""
            mock_response = Mock()
            if "orgs" in url:
                mock_response.json.return_value = cls.org_payload
            elif "repos" in url:
                mock_response.json.return_value = cls.repos_payload
            else:
                raise ValueError(f"Unexpected URL: {url}")
            return mock_response

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Integration test: public_repos should return all repo names
        from repos_payload, matching expected_repos.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """
        Integration test: public_repos(license="apache-2.0") should return
        only repos with apache-2.0 license, matching apache2_repos.
        """
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )
