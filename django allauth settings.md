# django allauth settings

1. install_app 跟 urls 都先設定好
2. 到/admin/裡面的social applications裡面新增facebook
3. 根據facebook api給的id, secrect key，依序填入
4. 要加入的site要看在setting.py裡面的`SITE_ID`是什麼，預設example.com的ID是1 (去database的djangoe_site看)
5. 在template裡面加上
	
	```
	{% load socialaccount %}
	<a href="{% provider_login_url "facebook" method="oauth2" %}">Facebook OAuth2</a>
	```

6. 可以在settings.py裡面再另外設定 `SOCIALACCOUNT_PROVIDERS` 調整facebook連結設定（看document）

7. 這樣應該就可以動了，可以去socialaccount_socialaccount裡面看有沒有要到資料
8. 記得在setting裡面把 LOGIN_REDIRECT_URL 設定成要的網址（預設是`/account/profile`）