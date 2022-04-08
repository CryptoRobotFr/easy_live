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

//permet d avoir plusieurs bot dans des folders differents
folder_name = os.path.basename(directory_path)

pip install -r folder_name/requirements.txt

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
$secret_content | jq '. + { "'"$strategy_name"'_'"$symbol1"'_'"$symbol2"'":{"public_key" : "'"$public_key"'","private_key" : "'"$private_key"'","subaccount_name" : "'"$subaccount_name"'","symbol1" : "'"$symbol1"'","symbol2" : "'"$symbol2"'"} }' secret.json > tmp.$$.json && mv tmp.$$.json secret.json

croncmd=" cd "$folder_name";python3 /"$strategy_name".py "$symbol1" "$symbol2" > cronlog.log"
cronjob="0 * * * * $croncmd"
( crontab -l | grep -v -F "$croncmd" ; echo "$cronjob" ) | crontab -

echo L erreur command not found n est pas un probleme

python3 "$folder_name"/"$strategy_name".py "$symbol1" "$symbol2"

echo Si votre programme vous a afficher un message qui ne ressemble pas a une erreur c est que tout est bien installe vous pouvez maintenant quitter par exemple en faisant par exemple la comande close
echo vous pouvez verifier que votre bot tourne en tapant \" crontab -l \" , vous aurez une ligne de type $croncmd
