PASS='user key'
USER='username'
ORG=cthit
repos=(hubbIT hubbIT-sniffer achieveIT bookIT playIT-grails misc auth wordpress dokument playIT-python chalmersit-wp-plugins Homestead chalmersit-rails chalmersit-account-rails CodeIT VoteIT HueIT-Rails nollkIT EatIT DreamTeamBots Hubben tv mat lounge)

for REPO in ${repos[@]}; do
    curl --user "$USER:$PASS" --include --request POST --data '{"name":"low","color":"2CA746"}' "https://api.github.com/repos/$ORG/$REPO/labels"
    curl --user "$USER:$PASS" --include --request POST --data '{"name":"medium","color":"FCBA00"}' "https://api.github.com/repos/$ORG/$REPO/labels"
    curl --user "$USER:$PASS" --include --request POST --data '{"name":"high","color":"ED422C"}' "https://api.github.com/repos/$ORG/$REPO/labels"
done
