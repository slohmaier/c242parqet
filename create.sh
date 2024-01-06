APP="python3 /Users/stefan/git/c242parqet/c242parqet.py"
HURL="https://app.parqet.com/p/651a793b2c2b7523b1be9de6/h/hld_659856c7617a474213bd0eb5"

for i in *.csv; do
    #ignore Parqet files
    if [[ $i == *"Parqet"* ]]; then
        continue
    fi
    echo "Processing $i"
    OUT=_$(echo "$i" | sed 's/\.csv/ Parqet.csv/g')
    $APP -c "$i" --hurl "$HURL" -p "$OUT" || exit 1
done
