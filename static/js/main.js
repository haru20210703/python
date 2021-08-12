//ページ内の時間表示場所の指定
	var nowtime = document.getElementById('nowtime');
//レスポンスヘッダーの読み込みを有効にするために変数設定
	var request = new XMLHttpRequest();
	var timer;
//setIntervalでこの処理を繰り返す設定
	timer = setInterval(function(){
//ページ読み込み時のレスポンスヘッダーからサーバーの時間を取得
	request.open('HEAD', window.location.href, true);
	request.send();
	request.onreadystatechange = function() {
		if(this.readyState === 4){
			var serverDate = new Date(request.getResponseHeader('Date'));
//取得したサーバー時間をdateに設定
			var date = new Date(serverDate);
//サーバー時間はunixtimestanp形式なので、そこから時、分、秒をそれぞれ取得して表示
			var nowHour = date.getHours();
			var nowMin = date.getMinutes();
			var nowSec = date.getSeconds();
			var msg = "現在時刻 " + nowHour + ":" + nowMin + ":" + nowSec;
			nowtime.innerHTML = msg;
			}
		}
//setIntervalの引数　javascriptでの時間表示は千分の一秒単位なので、1000にする事で一秒ごとの処理となる
	}, 1000);



