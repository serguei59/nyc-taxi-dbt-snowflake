CREATE SECURITY INTEGRATION GITHUB_OAUTH_INTEGRATION
  TYPE = EXTERNAL_OAUTH
  ENABLED = TRUE
  OAUTH_CLIENT = CUSTOM
  OAUTH_CLIENT_TYPE = 'CONFIDENTIAL'
  OAUTH_REDIRECT_URI = 'https://github.com/login/oauth'
  OAUTH_ISSUER = 'https://github.com'
  OAUTH_CLIENT_ID = '<ton_client_id>'
  OAUTH_CLIENT_SECRET = '<ton_client_secret>'
  OAUTH_CLIENT_AUTH_METHOD = 'CLIENT_SECRET_POST'
  OAUTH_TOKEN_ENDPOINT = 'https://github.com/login/oauth/access_token'
  OAUTH_AUTHORIZATION_ENDPOINT = 'https://github.com/login/oauth/authorize'
  OAUTH_ALLOWED_ROLES = ('ROLE_DBT_RUNNER', 'SYSADMIN')
  COMMENT = 'OAuth integration for GitHub Actions CI/CD';
