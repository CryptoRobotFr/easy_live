echo Quelle stratégie voulez vous installer ?
read strategy_name
echo Quelle le symbol du premier asset a trader ex pour BTC-USD il faut rentrer BTC ici ?
read symbol1
echo Quelle le symbol du deuxieme asset a trader ex pour BTC-USD il faut rentrer USD ici ?
read symbol2
echo Entrez votre clé api publique
read public_key
echo Entrez votre clé api privée
read private_key
echo Entrez le nom de votre sous compte, ne pas mettre despaces dans votre nom de sous compte!
read subaccount_name

sudo apt-get update
sudo apt install pip -y
sudo apt install jq -y
pip install -r easy_live/requirements.txt

secret_file=secret.json
if test -f "$secret_file"; then
    echo Conitu
else
    echo '{}' > secret.json
fi

cron_file=cronlog.log
if test -f "$secret_file"; then
    echo Conitu
else
    touch cronlog.log
fi

secret_content=`cat secret.json`
$secret_content | jq '. + { "'"$strategy_name"'":{"public_key" : "'"$public_key"'","private_key" : "'"$private_key"'","subaccount_name" : "'"$subaccount_name"'","symbol1" : "'"$symbol1"'","symbol2" : "'"$symbol2"'"} }' secret.json > tmp.$$.json && mv tmp.$$.json secret.json

croncmd="python3 easy_live/"$strategy_name".py > cronlog.log"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

echo L erreur comand not found n est pas un probleme

python3 easy_live/"$strategy_name".py

echo Si votre programme vous a afficher un message qui ne ressemble pas a une erreur c est que tout est bien installe vous pouvez maintenant quitter par exemple en faisant par exemple la comande close
