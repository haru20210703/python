#!bin/bash
#日時変数設定
YEAR=$(date +%Y)
MONTH=$(date +%-m)
DAY=$(date +%-d)
UNIX_TIME=$(date +%s)

#接続するデータベースの設定
MYSQL_DATABASE='blue'

#最後のログに残されたmacアドレスを取得
ROW=$(cat log.txt | wc -l)
MAC1=$(head -n $ROW log.txt | tail -n 1 | sed 's/^.*Device\(.*\)RSSI.*$/\1/')

#登録回数をカウントするための変数
N=0

#bluetoothctlが吐き出したログを読み取ってデータベースと参照する
while true
do
	#新しいログのmacアドレスを取得
	ROW=$(cat log.txt | wc -l)
	MAC2=$(head -n $ROW log.txt | tail -n 1 | sed 's/^.*Device\(.*\)RSSI.*$/\1/')
	MAC2=${MAC2// /}
	#前回取得したmacアドレスと違う場合は以下の処理に移る
	if [ "$MAC1" != "$MAC2" -a ${#MAC2} -lt 18 ]; then
	#新しく取得したmacアドレスからRSSI（受信強度）が取得出来ているなら以下の処理に移る
		#取得したmacアドレスを更新
		MAC1="$MAC2"
		MAC="$MAC2"

		#取得したログからmacアドレスのみを抽出

		#抽出したmacアドレスがデータベースに登録されているかの確認
		#--defaults-extra-fileで外部ファイルに登録しているデータベース接続情報を取得
		#-Nでカラム名無しでデータを取得
		SQL="SELECT mac FROM mac WHERE(mac = '$MAC');"
		MAC=`mysql --defaults-extra-file=./my.conf $MYSQL_DATABASE -N -e "${SQL}"`

		#macアドレスがデータベースに登録されていれば以下の処理に移る
		if [ ${#MAC} -gt 10 ]; then 

			#macアドレスのＩＤを取得
			SQL="SELECT id FROM mac WHERE(mac = '$MAC');"
			MAC_ID=`mysql --defaults-extra-file=./my.conf $MYSQL_DATABASE -N -e "${SQL}"`

			#ＩＤを記録用テーブルに登録
			SQL="INSERT INTO blue(mac_id) VALUES('$MAC_ID');"
			eval `mysql --defaults-extra-file=./my.conf $MYSQL_DATABASE -e "${SQL}"`

			#ＩＤから氏名を取得してプロンプトに表示
			SQL="SELECT name FROM mac WHERE(mac = '$MAC');"
			NAME=`mysql --defaults-extra-file=./my.conf $MYSQL_DATABASE -N -e "${SQL}"`
			echo $NAME

			#取得した氏名と時間をブラウザ表示用ファイルに出力
			IN_DATE=$(date +%Y%m%d_%H-%M-%S)
			sed -i "1s/^/$IN_DATE->$NAME\n/" /var/www/html/bt/log.html
			#20回同じ処理が繰り返されたらログを削除（データが増えるのを防止）
			N=$(($N + 1))
			if [ $N -ge 20 ]; then
				> log.html
				#echo 'rm log'
				N=0
			fi
		fi

		#取得したMACアドレスを出力
		echo $MAC1 >> /var/www/html/bt/mac.txt
		#echo $MAC1
		sort /var/www/html/bt/mac.txt | uniq > /var/www/html/bt/mac.html

	fi

	#ログが溜まったら削除
	LOG_LOW=$(cat /var/www/html/bt/log.html | wc -l)
	if [ $LOG_LOW -gt 30 ]; then
		echo $LOG_LOW
		sed -i '$d' /var/www/html/bt/log.html
	fi

	LOG_LOW=$(cat /var/www/html/bt/mac.txt | wc -l)
	if [ $LOG_LOW -gt 50 ]; then
		echo $LOG_LOW
		sed -i '$d' /var/www/html/bt/mac.txt
	fi
	
done
