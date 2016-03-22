# PASS: Your personal access token. Needs to have scope admin:repo_hook to work
# You can generate access tokens at https://github.com/settings/tokens
PASS='pass'
# USER: GitHub user name
USER='username'
ORG=cthit
repos=(hubbIT hubbIT-sniffer achieveIT bookIT playIT-grails misc auth wordpress dokument playIT-python chalmersit-wp-plugins Homestead chalmersit-rails chalmersit-account-rails CodeIT VoteIT HueIT-Rails nollkIT EatIT DreamTeamBots Hubben tv mat lounge)

DATA='{
  "name": "irc",
  "active": true,
  "events": [
    "pull_request",
    "issues",
    "issue_comment"
  ],
 "config": {
      "server": "irc.chalmers.it",
      "port": "9999",
      "room": "digit-support",
      "nick": "GitHubBot",
      "ssl": "1",
      "message_without_join": "1",
      "no_colors": "0",
      "long_url": "0",
      "notice": "0"
    }
}'


for REPO in ${repos[@]}; do
    curl --user "$USER:$PASS" --include --request POST --data "$DATA" "https://api.github.com/repos/$ORG/$REPO/hooks"
done